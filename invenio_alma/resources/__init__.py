# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio resources to connect InvenioRDM to Alma."""

from .config import AlmaResourceConfig
from .resources import AlmaResource

__all__ = (
    "AlmaResourceConfig",
    "AlmaResource",
)
