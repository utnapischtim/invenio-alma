# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the Alma-Connector module."""

import csv
import sys

# import logging
from os.path import isfile

import click
from click_option_group import optgroup
from flask.cli import with_appcontext
from invenio_records_marc21.records.systemfields import MarcDraftProvider
from sqlalchemy.orm.exc import StaleDataError

from .proxies import current_alma
from .utils import (
    AlmaConfig,
    RecordConfig,
    create_record,
    get_identity_from_user_by_email,
)

# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


class CSV(click.ParamType):
    """CSV provides the ability to load a csv from a file."""

    name = "CSV"

    def convert(self, value, param, ctx) -> csv.DictReader:
        """This method opens the files as a DictReader object."""
        if not isfile(value):
            click.secho("ERROR - please look up if the file path is correct.", fg="red")
            sys.exit()

        csv_file = open(value, mode="r", encoding="utf-8")
        reader = csv.DictReader(csv_file)

        return reader


def handle_csv(csv_file, alma_config, identity):
    """Process csv file."""
    for row in csv_file:
        if len(row["ac_number"]) == 0:
            continue

        if "marcid" in row and len(row["marcid"]) > 0:
            MarcDraftProvider.predefined_pid_value = row["marcid"]

        try:
            file_pointer = open(row["filename"], mode="rb")
            record_config = RecordConfig(row["ac_number"], file_pointer)

            record = create_record(alma_config, record_config, identity)
            print(f"record.id: {record.id}")
        except FileNotFoundError:
            print(f"FileNotFoundError search_value: {row['ac_number']}")
        except StaleDataError:
            print(f"StaleDataError    search_value: {row['ac_number']}")
            file_pointer.close()


def handle_single_import(ac_number, marcid, file_, alma_config, identity):
    """Process a single import of a alma record by ac number."""
    if marcid:
        MarcDraftProvider.predefined_pid_value = marcid

    record_config = RecordConfig(ac_number, file_)
    try:
        record = create_record(alma_config, record_config, identity)
        print(f"record.id: {record.id}")
    except StaleDataError:
        print(f"StaleDataError    search_value: {ac_number}")


@click.group()
def alma():
    """Alma CLI."""


# @alma.command()
# @click.option("--mms-id", type=click.STRING, required=True)
# def show(mms_id):
#     """Show entry by mms_id."""


@alma.command()
@with_appcontext
@optgroup.group("Request Configuration", help="The Configuration for the request")
@optgroup.option("--search-key", type=click.STRING, required=True)
@optgroup.option("--domain", type=click.STRING, required=True)
@optgroup.option("--institution-code", type=click.STRING, required=True)
@optgroup.group("Manually set the values to search and import")
@optgroup.option("--ac-number", type=click.STRING)
@optgroup.option("--file", "file_", type=click.File("rb"))
@optgroup.option("--user-email", type=click.STRING, default="alma@tugraz.at")
@optgroup.option("--marcid", type=click.STRING, default="")
@optgroup.group("Import by file list")
@optgroup.option("--csv-file", type=CSV())
def sru(
    search_key, domain, institution_code, ac_number, file_, user_email, marcid, csv_file
):
    """Search on the SRU service of alma."""
    alma_config = AlmaConfig(search_key, domain, institution_code)
    identity = get_identity_from_user_by_email(email=user_email)

    if csv_file:
        handle_csv(csv_file, alma_config, identity)
    else:
        handle_single_import(ac_number, marcid, file_, alma_config, identity)


@alma.command("update-url-in-alma")
@with_appcontext
@click.option("--user-email", type=click.STRING, required=True)
@click.option("--url", type=click.STRING, required=True)
def update_url_in_alma(user_email, url):
    """Update url in remote repository records.

    :params user_email (str): username to authenticate
    :params url (str): new repository url. Url must contain '{recid}'
    """
    identity = get_identity_from_user_by_email(email=user_email)
    records = current_alma.repository_service.get_records(identity)
    current_alma.alma_service.update_url(records, url)
