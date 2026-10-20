# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Invenio module to connect InvenioRDM to Alma."""

from .ext import InvenioAlma
from .services import AlmaRESTService, AlmaSRUService

__version__ = "0.15.0"

__all__ = (
    "AlmaRESTService",
    "AlmaSRUService",
    "InvenioAlma",
    "__version__",
)
