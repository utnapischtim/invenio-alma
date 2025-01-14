# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to connect InvenioRDM to Alma."""

from . import config


class InvenioAlma:
    """invenio-alma extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["invenio-alma"] = self

    def init_config(self, app):  # pylint: disable=no-self-use
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("INVENIO_ALMA_"):
                app.config.setdefault(k, getattr(config, k))
