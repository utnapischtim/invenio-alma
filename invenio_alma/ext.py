# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to connect InvenioRDM to Alma."""

from __future__ import annotations

from dataclasses import dataclass

from flask import Blueprint, Flask, current_app

from .resources import AlmaResource, AlmaResourceConfig
from .services import AlmaRESTService, AlmaSRUService
from .services.config import AlmaRESTConfig, AlmaSRUConfig


@dataclass(frozen=True)
class AlmaResourceMock:
    """Alma Resource Mock class. It is used if the alma resource is not initialized."""

    def as_blueprint(self) -> Blueprint:
        """Return a mocked Blueprint object."""
        return Blueprint("AlmaResourceMockBlueprint", __name__)


class InvenioAlma:
    """invenio-alma extension."""

    def __init__(self, app: Flask = None) -> None:
        """Extension initialization."""
        self._alma_rest_service = None
        self._alma_resource = None

        if app:
            self.init_app(app)

    @property
    def alma_rest_service(self) -> AlmaRESTService:
        """Return the alma rest service."""
        if not self._alma_rest_service:
            current_app.logger.warn("AlmaRESTService was not initialized correctly.")
            config = AlmaRESTConfig("", "")
            return AlmaRESTService(config=config)

        return self._alma_rest_service

    @property
    def alma_sru_service(self) -> AlmaSRUService:
        """Get alma sru service."""
        return self._alma_sru_service

    @property
    def alma_resource(self) -> AlmaResource | AlmaResourceMock:
        """Return the alma resource."""
        if not self._alma_resource:
            current_app.logger.warn("AlmaResources was not initialized correctly.")
            return AlmaResourceMock()

        return self._alma_resource

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        self.init_services(app)
        self.init_resources(app)
        app.extensions["invenio-alma"] = self

    def init_services(self, app: Flask) -> None:
        """Initialize service."""
        api_key = app.config.get("ALMA_API_KEY", "")
        api_host = app.config.get("ALMA_API_HOST", "")
        rest_config = AlmaRESTConfig(api_key, api_host)

        domain = app.config["ALMA_SRU_DOMAIN"]
        institution_code = app.config["ALMA_SRU_INSTITUTION_CODE"]
        sru_config = AlmaSRUConfig("", domain, institution_code)

        self._alma_rest_service = AlmaRESTService(config=rest_config)
        self._alma_sru_service = AlmaSRUService(config=sru_config)

    def init_resources(self, app: Flask) -> None:
        """Initialize resources."""
        search_key = "local_control_field_009"  # ac_number
        domain = app.config.get("ALMA_SRU_DOMAIN")
        institution_code = app.config.get("ALMA_SRU_INSTITUTION_CODE")
        config = AlmaSRUConfig(search_key, domain, institution_code)

        self._alma_resource = AlmaResource(
            service=AlmaSRUService(config=config),
            config=AlmaResourceConfig,
        )
