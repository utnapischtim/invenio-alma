# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Alma Views module."""


def create_record_bp(app):
    """Create records blueprint."""
    ext = app.extensions["invenio-alma"]
    return ext.alma_resource.as_blueprint()
