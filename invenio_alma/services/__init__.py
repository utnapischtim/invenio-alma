# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio service to connect InvenioRDM to Alma."""

from .errors import AlmaAPIError, AlmaRESTError
from .rest import AlmaRESTService
from .sru import AlmaSRUService

__all__ = (
    "AlmaRESTService",
    "AlmaSRUService",
    "AlmaRESTError",
    "AlmaAPIError",
)
