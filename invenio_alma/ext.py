# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to connect InvenioRDM to Alma."""

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from flask import Flask

from .resources import AlmaResource, AlmaResourceConfig
from .services import AlmaRESTService, AlmaSRUService


class InvenioAlma:
    """invenio-alma extension."""

    def __init__(self, app: Flask = None) -> None:
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        self.init_services(app)
        self.init_resources(app)
        app.extensions["invenio-alma"] = self

    def init_services(self, app: Flask) -> None:
        """Initialize service."""
        api_key = app.config.get("ALMA_API_KEY", "")
        api_host = app.config.get("ALMA_API_HOST", "")

        self.alma_rest_service = AlmaRESTService.build(api_key, api_host)

    def init_resources(self, app: Flask) -> None:
        """Initialize resources."""
        search_key = "local_control_field_009"  # ac_number
        domain = app.config.get("ALMA_SRU_DOMAIN")
        institution_code = app.config.get("ALMA_SRU_INSTITUTION_CODE")
        self.alma_resource = AlmaResource(
            service=AlmaSRUService.build(search_key, domain, institution_code),
            config=AlmaResourceConfig,
        )
