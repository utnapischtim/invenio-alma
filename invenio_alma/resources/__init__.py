# SPDX-FileCopyrightText: 2023-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Invenio resources to connect InvenioRDM to Alma."""

from .config import AlmaResourceConfig
from .resources import AlmaResource

__all__ = (
    "AlmaResource",
    "AlmaResourceConfig",
)
