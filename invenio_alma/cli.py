# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
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

from .utils import create_record

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

        csv_file = open(value)
        reader = csv.DictReader(csv_file)

        return reader


@click.group()
def alma():
    """Alma CLI."""


@alma.command()
@click.option("--mms-id", type=click.STRING, required=True)
def show(mms_id):
    pass


@alma.command()
@with_appcontext
@optgroup.group("Request Configuration", help="The Configuration for the request")
@optgroup.option("--search-key", type=click.STRING, required=True)
@optgroup.option("--domain", type=click.STRING, required=True)
@optgroup.option("--institution-code", type=click.STRING, required=True)
@optgroup.group("Manually set the values to search and import")
@optgroup.option("--search-value", type=click.STRING)
@optgroup.option("--file", "file_", type=click.File("rb"))
@optgroup.option("--user", type=click.STRING, default="alma@tugraz.at")
@optgroup.option("--marcid", type=click.STRING, default="")
@optgroup.group("Import by file list")
@optgroup.option("--csv", type=CSV())
def sru(search_key, domain, institution_code, search_value, file_, user, marcid, csv):
    """Search on the SRU service of alma."""

    if csv:
        for row in csv:
            if len(row["search_value"]) == 0:
                continue

            if "marcid" in row and len(row["marcid"]) > 0:
                MarcDraftProvider.predefined_pid_value = row["marcid"]

            try:
                fp = open(row["filename"], "rb")
                record = create_record(
                    search_key, domain, institution_code, row["search_value"], fp
                )
                print(f"record.id: {record.id}")
                fp.close()
            except FileNotFoundError:
                print(
                    f"FileNotFoundError search_value: {row['search_value']}, filename: {row['filename']}"
                )
            except StaleDataError:
                print(
                    f"StaleDataError    search_value: {row['search_value']}, filename: {row['filename']}"
                )

    else:
        if marcid:
            MarcDraftProvider.predefined_pid_value = marcid

        record = create_record(
            search_key, domain, institution_code, search_value, file_
        )
        print(f"record.id: {record.id}")


@alma.command()
@with_appcontext
def file_upload(ac, marcid, filename):
    pass
