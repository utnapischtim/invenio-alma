# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Click param types."""
import sys
from csv import DictReader
from io import TextIOWrapper
from json import JSONDecodeError, load, loads
from pathlib import Path
from typing import Any

from click import Context, Parameter, ParamType, secho


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
        value: Any,
        param: Parameter | None,  # noqa: ARG002
        ctx: Context | None,  # noqa: ARG002
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


####
# copy pasted from repository-cli
# code slightly updated
###
def _error_msg(art: str, key: str) -> str:
    """Construct error message."""
    error_msgs = {
        "validate": f"The given json does not validate, key: '{key}' does not exists",
    }
    return error_msgs[art]


class JSON(ParamType):
    """JSON provides the ability to load a json from a string or a file."""

    name = "JSON"

    def __init__(self, validate: list[str] | None = None) -> None:
        """Construct Json ParamType."""
        self.validate = validate

    def convert(
        self,
        value: Any,
        param: Parameter | None,  # noqa: ARG002
        ctx: Context | None,  # noqa: ARG002
    ) -> Any:
        """The method converts the json-file to the dictionary representation."""
        try:
            if Path(value).is_file():
                with Path(value).open("r", encoding="utf8") as file_pointer:
                    obj = load(file_pointer)
            else:
                obj = loads(value)
        except JSONDecodeError as error:
            msg = "ERROR - Invalid JSON provided. Check file path or json string."
            secho(msg, fg="red")
            secho(f"  error: {error.args[0]}", fg="red")
            sys.exit()

        if self.validate:
            for key in self.validate:
                if key not in obj:
                    secho(_error_msg("validate", key), fg="red")
                    sys.exit()

        return obj


####
# copy pasted from repository-cli END
###
