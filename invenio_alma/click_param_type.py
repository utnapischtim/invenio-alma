# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Click param types."""

import sys
from csv import DictReader
from os.path import isfile

from click import ParamType, secho


class CSV(ParamType):
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
            secho("ERROR - please look up if the file path is correct.", fg="red")
            sys.exit()

        csv_file = open(value, mode="r", encoding="utf-8")
        reader = DictReader(csv_file)

        if self.check_header and not self.is_header_as_expected(csv_file):
            msg = f"ERROR - the header should have the form: {self.header}."
            secho(msg, fg="red")
            sys.exit()

        return reader
