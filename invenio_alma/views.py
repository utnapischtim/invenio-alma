# SPDX-FileCopyrightText: 2023-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alma Views module."""

from typing import cast

from flask import Blueprint, Flask


def create_record_bp(app: Flask) -> Blueprint:
    """Create records blueprint."""
    ext = app.extensions["invenio-alma"]
    return cast(Blueprint, ext.alma_resource.as_blueprint())
