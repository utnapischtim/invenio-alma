# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to connect InvenioRDM to Alma."""

from .ext import InvenioAlma
from .services import AlmaRESTService, AlmaSRUService

__version__ = "0.11.1"

__all__ = ("__version__", "InvenioAlma", "AlmaSRUService", "AlmaRESTService")
