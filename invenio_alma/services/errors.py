# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Services exceptions."""


class AlmaException(Exception):
    """Base exception for Alma errors."""


class AlmaRESTException(AlmaException):
    """Alma Rest API exception class."""

    def __init__(self, code, msg):
        """Initialise error."""
        super().__init__(f"Alma API error code={code} msg='{msg}'")
