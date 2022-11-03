# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the Alma-Connector module."""

import sys
from csv import DictReader
from os.path import isfile
from time import sleep

import click
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
from flask.cli import with_appcontext
from invenio_config_tugraz import get_identity_from_user_by_email
from invenio_records_marc21 import (
    Marc21Metadata,
    MarcDraftProvider,
    create_record,
    current_records_marc21,
)
from invenio_search import RecordsSearch
from invenio_search.engine import dsl
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import StaleDataError

from .proxies import current_alma
from .services import AlmaSRUService
from .utils import create_alma_record as _create_alma_record
from .utils import preliminaries
from .utils import update_repository_record as _update_repository_record


class DuplicateRecordError(Exception):
    """Duplicate Record Exception."""

    def __init__(self, ac_number, id_):
        """Constructor for class DuplicateRecordException."""
        msg = f"DuplicateRecordError ac_number: {ac_number} already exists id={id_} in the database"
        super().__init__(msg)


class CSV(click.ParamType):
    """CSV provides the ability to load a csv from a file."""

    name = "CSV"

    def __init__(self, header=None):
        """Constructor of CSV type."""
        super().__init__()
        self.header = header
        self.check_header = header is not None

    @property
    def headers(self):
        """Headers."""
        return self.header.split(",")

    def is_header_as_expected(self, csv_file):
        """Check if the header is as expected."""
        reader = DictReader(csv_file)
        first_row = next(reader)
        # because iterator has no previous method
        csv_file.seek(0)

        return all(name in first_row for name in self.headers)

    def convert(self, value, param, ctx) -> DictReader:
        """This method opens the files as a DictReader object."""
        if not isfile(value):
            click.secho("ERROR - please look up if the file path is correct.", fg="red")
            sys.exit()

        csv_file = open(value, mode="r", encoding="utf-8")
        reader = DictReader(csv_file)

        if self.check_header and not self.is_header_as_expected(csv_file):
            msg = f"ERROR - the header should have the form: {self.header}."
            click.secho(msg, fg="red")
            sys.exit()

        return reader


# TODO:
# move to invenio-records-marc21
def check_about_duplicate(ac_number):
    """Check if the record with the ac number is already within the database."""
    search = RecordsSearch(index="marc21records-marc21")
    search.query = dsl.Q("match", **{"metadata.fields.009": ac_number})
    results = search.execute()

    if len(results) > 0:
        raise DuplicateRecordError(ac_number=ac_number, id_=results[0]["id"])


def handle_csv(alma_sru_service, csv_file, identity):
    """Process csv file."""
    for row in csv_file:
        if len(row["ac_number"]) == 0:
            continue

        handle_single_import(alma_sru_service, **row, identity=identity)


# pylint: disable-next=too-many-return-statements)
def handle_single_import(
    alma_sru_service, ac_number, file_path, identity, marcid=None, **_
):
    """Process a single import of a alma record by ac number."""
    if marcid:
        MarcDraftProvider.predefined_pid_value = marcid

    service = current_records_marc21.records_service

    retry_counter = 0
    while True:
        try:
            check_about_duplicate(ac_number)

            marc21_record = Marc21Metadata(alma_sru_service.get_record(ac_number))
            record = create_record(service, marc21_record, file_path, identity)

            print(f"record.id: {record.id}, ac_number: {ac_number}")
            return
        except FileNotFoundError:
            print(f"FileNotFoundError search_value: {ac_number}")
            return
        except DuplicateRecordError as error:
            print(error)
            return
        except StaleDataError:
            print(f"StaleDataError    search_value: {ac_number}")
            return
        except ValidationError:
            print(f"ValidationError   search_value: {ac_number}")
            return
        except dsl.RequestError:
            print(f"RequestError      search_value: {ac_number}")
            return
        except dsl.ConnectionTimeout:
            msg = f"ConnectionTimeout search_value: {ac_number}, retry_counter: {retry_counter}"
            print(msg)

            # cool down the elasticsearch indexing process. necessary for
            # multiple imports in a short timeframe
            sleep(100)

            # don't overestimate the problem. if three rounds doesn't help go to
            # the next ac number
            if retry_counter > 3:
                return
            retry_counter += 1


@click.group()
def alma():
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
    search_key,
    domain,
    institution_code,
    ac_number,
    filename,
    user_email,
    marcid,
    csv_file,
):
    """Search on the SRU service of alma."""
    identity = get_identity_from_user_by_email(email=user_email)
    alma_sru_service = AlmaSRUService.build(search_key, domain, institution_code)

    if csv_file:
        handle_csv(alma_sru_service, csv_file, identity)
    else:
        handle_single_import(alma_sru_service, ac_number, filename, identity, marcid)


@alma.command("update-url-in-alma")
@with_appcontext
@click.option(
    "--csv-file",
    type=CSV(header="mms_id,new_url"),
    required=True,
    help="two columns: mms_id and new_url",
)
def update_url_in_alma(csv_file):
    """Update url in remote repository records.

    :params csv_file (file) with two columns mms_id and new_url
    """
    for row in csv_file:
        current_alma.alma_rest_service.update_field(
            row["mms_id"], "856.4._.u", row["new_url"]
        )


@alma.command()
@with_appcontext
@click.option("--mms-id", type=click.STRING, required=True)
@click.option(
    "--field-json-path", type=click.STRING, required=True, help="e.g. 100.1._.u"
)
@click.option("--subfield-value", type=click.STRING, default="")
@click.option("--new-subfield-value", type=click.STRING, required=True)
@click.option(
    "--new-subfield-template",
    type=click.STRING,
    help="the template is given as json path 100.2.1.u",
    default="",
)
def update_field(
    mms_id, field_json_path, subfield_value, new_subfield_value, new_subfield_template
):
    """Update field."""
    current_alma.alma_rest_service.update_field(
        mms_id,
        field_json_path,
        new_subfield_value,
        subfield_value,
        new_subfield_template,
    )


@alma.group()
def create():
    """Alma Create group."""


@create.command("alma-record")
@with_appcontext
@click.option("--marc-id", type=click.STRING, required=True)
@click.option("--user-email", type=click.STRING, default="alma@tugraz.at")
@click.option("--api-key", type=click.STRING, required=True)
def create_alma_record(marc_id, user_email, api_key):
    """Create alma record."""

    records_service, alma_service, identity = preliminaries(user_email, use_rest=True)

    alma_service.config.api_key = api_key

    _create_alma_record(records_service, alma_service, identity, marc_id)


@create.command("repository-record")
@click.option("--mms-id", type=click.STRING, required=True)
def create_repository_record(mms_id):  # pylint: disable=unused-argument
    """Create repository record."""
    print("not yet implemented")
    # TODO:
    # create a record within the repository from an existing alma record
    # with mms_id=[MMS_ID]
    # use service provided by invenio-records-marc21 to create the record

    # SKETCH
    # record = current_alma.record_service.get_record(mms_id)

    # TODO:
    # massage data to move 001 mms-id to 035__a (tugraz)mms-id

    # current_records_marc21.record_service.create_record()


@alma.group()
def update():
    """Alma update group."""


@update.command("repository-record")
@with_appcontext
@click.option("--marc-id", type=click.STRING, required=True)
@click.option("--user-email", type=click.STRING, default="alma@tugraz.at")
@click.option("--api-key", type=click.STRING, required=True)
@optgroup.group("Alma identifier", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--mms-id", type=click.STRING, help="mms-id", default=None)
@optgroup.option("--thesis-id", type=click.STRING, help="thesis-id", default=None)
def update_repository_record(marc_id, user_email, api_key, mms_id, thesis_id):
    """Update Repository record."""

    if mms_id:
        use_rest = True
        alma_thesis_id = mms_id
    elif thesis_id:
        use_sru = True
        alma_thesis_id = thesis_id
    else:
        raise RuntimeError("Neither of mms_id and thesis_id were given.")

    records_service, alma_service, identity = preliminaries(
        user_email, use_rest=use_rest, use_sru=use_sru
    )

    alma_service.config.api_key = api_key

    _update_repository_record(
        records_service, alma_service, marc_id, identity, alma_thesis_id
    )
