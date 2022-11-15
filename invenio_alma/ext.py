# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to connect InvenioRDM to Alma."""

from . import config
from .services import AlmaRESTService


class InvenioAlma:
    """invenio-alma extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        app.extensions["invenio-alma"] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault("CELERY_BEAT_SCHEDULE", {})

        for k in dir(config):
            if k == "ALMA_CELERY_BEAT_SCHEDULE":
                app.config["CELERY_BEAT_SCHEDULE"].update(getattr(config, k))

            elif k.startswith("ALMA_"):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Initialize service."""
        api_key = app.config["ALMA_API_KEY"]
        api_host = app.config["ALMA_API_HOST"]

        if api_key == "" or api_host == "":
            raise RuntimeError(
                "ALMA_API_KEY and ALMA_API_HOST has to have a non empty value"
            )

        self.alma_rest_service = AlmaRESTService.build(api_key, api_host)
