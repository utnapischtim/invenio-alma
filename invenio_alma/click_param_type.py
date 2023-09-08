# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Click param types."""
from __future__ import annotations

import sys
from csv import DictReader
from io import TextIOWrapper
from pathlib import Path
from typing import Any

from click import ParamType, secho


class CSV(ParamType):
    """CSV provides the ability to load a csv from a file."""

    name = "CSV"

    def __init__(self, header: str | None = None) -> None:
        """Create type CSV."""
        super().__init__()
        self.header = header
        self.check_header = header is not None

    @property
    def headers(self) -> list[str]:
        """Headers."""
        return self.header.split(",")

    def is_header_as_expected(self, csv_file: TextIOWrapper) -> bool:
        """Check if the header is as expected."""
        reader = DictReader(csv_file)
        first_row = next(reader)
        # because iterator has no previous method
        csv_file.seek(0)

        return all(name in first_row for name in self.headers)

    def convert(
        self,
        value: Any,  # noqa: ANN401
        param: Any,  # noqa: ANN401, ARG002
        ctx: Any,  # noqa: ANN401, ARG002
    ) -> DictReader:
        """Convert filename in value to an DictReader object."""
        if not Path(value).is_file():
            secho("ERROR - please look up if the file path is correct.", fg="red")
            sys.exit()

        csv_file = Path(value).open(mode="r", encoding="utf-8")  # noqa: SIM115
        reader = DictReader(csv_file)

        if self.check_header and not self.is_header_as_expected(csv_file):
            msg = f"ERROR - the header should have the form: {self.header}."
            secho(msg, fg="red")
            sys.exit()

        return reader
