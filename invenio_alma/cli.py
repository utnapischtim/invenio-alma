# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the Alma-Connector module."""

from click import STRING, group, option, secho
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
from flask import current_app
from flask.cli import with_appcontext
from invenio_config_tugraz import get_identity_from_user_by_email
from invenio_records_marc21 import current_records_marc21

from .api import import_record
from .click_param_type import CSV
from .proxies import current_alma
from .services import AlmaRESTService, AlmaSRUService
from .services.config import AlmaRESTConfig, AlmaSRUConfig
from .types import Color


@group()
def alma() -> None:
    """Alma CLI."""


@alma.command()
@with_appcontext
@optgroup.group("Request Configuration", help="The Configuration for the request")
@optgroup.option("--search-key", type=STRING, required=True)
@optgroup.option("--domain", type=STRING, required=True)
@optgroup.option("--institution-code", type=STRING, required=True)
@optgroup.group("Manually set the values to search and import")
@optgroup.option("--ac-number", type=STRING)
@optgroup.option("--filename", type=STRING)
@optgroup.option("--access", type=STRING)
@optgroup.option("--user-email", type=STRING, default="alma@tugraz.at")
@optgroup.option("--marcid", type=STRING, default="")
@optgroup.group("Import by file list")
@optgroup.option("--csv-file", type=CSV())
def import_using_sru(
    search_key: str,
    domain: str,
    institution_code: str,
    ac_number: str,
    filename: str,
    access: str,
    user_email: str,
    marcid: str,
    csv_file: CSV,
) -> None:
    """Search on the SRU service of alma."""
    identity = get_identity_from_user_by_email(email=user_email)
    config = AlmaSRUConfig(search_key, domain, institution_code)
    alma_service = AlmaSRUService(config)
    record_service = current_records_marc21.records_service

    if csv_file:
        list_of_items = csv_file
    else:
        list_of_items = [
            {
                "ac_number": ac_number,
                "access": access,
                "file_path": filename,
                "marcid": marcid,
            },
        ]

    for row in list_of_items:
        if len(row["ac_number"]) == 0:
            continue

        ret = import_record(record_service, alma_service, **row, identity=identity)
        secho(ret["msg"], fg=ret["color"])


@alma.group()
def create() -> None:
    """Alma Create group."""


@create.command("alma-record")
@with_appcontext
@option("--marc-id", type=STRING, required=True)
@option("--user-email", type=STRING, default="alma@tugraz.at")
@option("--api-key", type=STRING, required=True)
@option("--api-host", type=STRING, required=True)
@option("--cms-id", type=STRING, required=True)
def cli_create_alma_record(
    marc_id: str,
    user_email: str,
    api_key: str,
    api_host: str,
    cms_id: str,
) -> None:
    """Create alma record."""
    config = AlmaRESTConfig(api_key, api_host)
    alma_service = AlmaRESTService(config=config)
    records_service = current_records_marc21.records_service
    identity = get_identity_from_user_by_email(email=user_email)

    create_func = current_app.config.get("ALMA_ALMA_RECORDS_CREATE_FUNC")
    create_func(records_service, alma_service, identity, marc_id, cms_id)


@alma.group()
def update() -> None:
    """Alma update group."""


@update.command("repository-record")
@with_appcontext
@option("--marc-id", type=STRING, required=True)
@option("--user-email", type=STRING, default="alma@tugraz.at")
@optgroup.group("Alma REST config")
@optgroup.option("--api-key", type=STRING)
@optgroup.option("--api-host", type=STRING)
@optgroup.group("Alma SRU config")
@optgroup.option("--search-key", type=STRING)
@optgroup.option("--domain", type=STRING)
@optgroup.option("--institution-code", type=STRING)
@optgroup.group("Alma identifier", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--mms-id", type=STRING, help="mms-id", default=None)
@optgroup.option("--thesis-id", type=STRING, help="thesis-id", default=None)
def cli_update_repository_record(
    marc_id: str,
    user_email: str,
    api_key: str,
    api_host: str,
    search_key: str,
    domain: str,
    institution_code: str,
    mms_id: str,
    thesis_id: str,
) -> None:
    """Update Repository record."""
    if mms_id:
        alma_thesis_id = mms_id
        config = AlmaRESTConfig(api_key, api_host)
        alma_service = AlmaRESTService(config=config)
    elif thesis_id:
        alma_thesis_id = thesis_id
        config = AlmaSRUConfig(search_key, domain, institution_code)
        alma_service = AlmaSRUService(config=config)
    else:
        msg = "Neither of mms_id and thesis_id were given."
        secho(msg, fg=Color.error)

    records_service = current_records_marc21.records_service
    identity = get_identity_from_user_by_email(email=user_email)
    update_func = current_app.config.get("ALMA_REPOSITORY_RECORDS_UPDATE_FUNC")
    update_func(records_service, alma_service, marc_id, alma_thesis_id, identity)


@update.command("url-in-alma")
@with_appcontext
@option(
    "--csv-file",
    type=CSV(header="mms_id,new_url"),
    required=True,
    help="two columns: mms_id and new_url",
)
def update_url_in_alma(csv_file: CSV) -> None:
    """Update url in remote repository records.

    :params csv_file (file) with two columns mms_id and new_url
    """
    for mms_id, new_url in csv_file:
        current_alma.alma_rest_service.update_field(mms_id, "856.4._.u", new_url)


@update.command("field")
@with_appcontext
@option("--mms-id", type=STRING, required=True)
@option(
    "--field-json-path",
    type=STRING,
    required=True,
    help="e.g. 100.1._.u",
)
@option("--new-subfield-value", type=STRING, required=True)
def update_field(mms_id: str, field_json_path: str, new_subfield_value: str) -> None:
    """Update field."""
    service = current_alma.alma_rest_service
    service.update_field(mms_id, field_json_path, new_subfield_value)
