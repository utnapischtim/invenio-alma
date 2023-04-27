# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Alma Views module."""

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from flask import Blueprint, Flask


def create_record_bp(app: Flask) -> Blueprint:
    """Create records blueprint."""
    ext = app.extensions["invenio-alma"]
    return ext.alma_resource.as_blueprint()
