# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Services exceptions."""


class AlmaAPIError(Exception):
    """Alma API error class."""

    def __init__(self, code: int, msg: str) -> None:
        """Create alma api error."""
        super().__init__(f"Alma API error code={code} msg='{msg}'")


class AlmaRESTError(Exception):
    """Alma Rest API error class."""

    def __init__(self, code: int, msg: str) -> None:
        """Create alma rest error."""
        super().__init__(f"Alma REST error code={code} msg='{msg}'")


class AlmaSRUError(Exception):
    """Alma SRU error class."""

    def __init__(self, code: int, msg: str) -> None:
        """Create alma sru error."""
        super().__init__(f"Alma SRU error code={code} msg='{msg}'")
