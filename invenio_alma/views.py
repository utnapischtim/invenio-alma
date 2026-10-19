# SPDX-FileCopyrightText: 2023-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alma Views module."""

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from flask import Blueprint, Flask


def create_record_bp(app: Flask) -> Blueprint:
    """Create records blueprint."""
    ext = app.extensions["invenio-alma"]
    return ext.alma_resource.as_blueprint()
