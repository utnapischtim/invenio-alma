# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the Alma-Connector module."""

import click
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
from flask import current_app
from flask.cli import with_appcontext
from invenio_config_tugraz import get_identity_from_user_by_email

from .api import (
    create_alma_record,
    import_list_of_records,
    import_record,
    update_repository_record,
)
from .click_param_type import CSV
from .proxies import current_alma
from .services import AlmaSRUService
from .services.config import AlmaRESTConfig, AlmaSRUConfig
from .utils import preliminaries


@click.group()
def alma() -> None:
    """Alma CLI."""


@alma.command()
@with_appcontext
@optgroup.group("Request Configuration", help="The Configuration for the request")
@optgroup.option("--search-key", type=click.STRING, required=True)
@optgroup.option("--domain", type=click.STRING, required=True)
@optgroup.option("--institution-code", type=click.STRING, required=True)
@optgroup.group("Manually set the values to search and import")
@optgroup.option("--ac-number", type=click.STRING)
@optgroup.option("--filename", type=click.STRING)
@optgroup.option("--user-email", type=click.STRING, default="alma@tugraz.at")
@optgroup.option("--marcid", type=click.STRING, default="")
@optgroup.group("Import by file list")
@optgroup.option("--csv-file", type=CSV())
def sru(
    search_key: str,
    domain: str,
    institution_code: str,
    ac_number: str,
    filename: str,
    user_email: str,
    marcid: str,
    csv_file: CSV,
) -> None:
    """Search on the SRU service of alma."""
    identity = get_identity_from_user_by_email(email=user_email)
    alma_sru_service = AlmaSRUService.build(search_key, domain, institution_code)

    if csv_file:
        import_list_of_records(alma_sru_service, csv_file, identity)
    else:
        import_record(alma_sru_service, ac_number, filename, identity, marcid)


@alma.group()
def create() -> None:
    """Alma Create group."""


@create.command("alma-record")
@with_appcontext
@click.option("--marc-id", type=click.STRING, required=True)
@click.option("--user-email", type=click.STRING, default="alma@tugraz.at")
@click.option("--api-key", type=click.STRING, required=True)
@click.option("--api-host", type=click.STRING, required=True)
@click.option("--cms-id", type=click.STRING, required=True)
def cli_create_alma_record(
    marc_id: str,
    user_email: str,
    api_key: str,
    api_host: str,
    cms_id: str,
) -> None:
    """Create alma record."""
    config = AlmaRESTConfig(api_key, api_host)

    records_service, alma_service, identity = preliminaries(
        user_email,
        config,
        use_rest=True,
        use_sru=False,
    )
    create_alma_record(records_service, alma_service, identity, marc_id, cms_id)


@alma.group()
def update() -> None:
    """Alma update group."""


@update.command("repository-record")
@with_appcontext
@click.option("--marc-id", type=click.STRING, required=True)
@click.option("--user-email", type=click.STRING, default="alma@tugraz.at")
@optgroup.group("Alma REST config")
@optgroup.option("--api-key", type=click.STRING)
@optgroup.option("--api-host", type=click.STRING)
@optgroup.group("Alma SRU config")
@optgroup.option("--search-key", type=click.STRING)
@optgroup.option("--domain", type=click.STRING)
@optgroup.option("--institution-code", type=click.STRING)
@optgroup.group("Alma identifier", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--mms-id", type=click.STRING, help="mms-id", default=None)
@optgroup.option("--thesis-id", type=click.STRING, help="thesis-id", default=None)
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
    use_rest = False
    use_sru = False

    if mms_id:
        use_rest = True
        alma_thesis_id = mms_id
        config = AlmaRESTConfig(api_key, api_host)
    elif thesis_id:
        use_sru = True
        alma_thesis_id = thesis_id
        config = AlmaSRUConfig(search_key, domain, institution_code)
    else:
        msg = "Neither of mms_id and thesis_id were given."
        raise RuntimeError(msg)

    update_func = current_app.config.get("ALMA_REPOSITORY_RECORDS_UPDATE_FUNC", None)

    records_service, alma_service, identity = preliminaries(
        user_email,
        config,
        use_rest=use_rest,
        use_sru=use_sru,
    )

    if update_func:
        update_func(records_service, alma_service, marc_id, thesis_id, identity)
    else:
        update_repository_record(
            records_service,
            alma_service,
            marc_id,
            identity,
            alma_thesis_id,
        )


@update.command("url-in-alma")
@with_appcontext
@click.option(
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
@click.option("--mms-id", type=click.STRING, required=True)
@click.option(
    "--field-json-path",
    type=click.STRING,
    required=True,
    help="e.g. 100.1._.u",
)
@click.option("--new-subfield-value", type=click.STRING, required=True)
def update_field(mms_id: str, field_json_path: str, new_subfield_value: str) -> None:
    """Update field."""
    service = current_alma.alma_rest_service
    service.update_field(mms_id, field_json_path, new_subfield_value)
