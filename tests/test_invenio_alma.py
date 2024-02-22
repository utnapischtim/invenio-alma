# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_alma import InvenioAlma, __version__


def test_version() -> None:
    """Test version import."""
    assert __version__


def test_init() -> None:
    """Test extension initialization."""
    app = Flask("testapp")
    app.config["ALMA_API_KEY"] = "test-token"
    app.config["ALMA_API_HOST"] = "test-host"

    app.config["ALMA_SRU_DOMAIN"] = "test-host"
    app.config["ALMA_SRU_INSTITUTION_CODE"] = "test-code"

    ext = InvenioAlma(app)
    assert "invenio-alma" in app.extensions

    app = Flask("testapp")
    app.config["ALMA_API_KEY"] = "test-token"
    app.config["ALMA_API_HOST"] = "test-host"

    app.config["ALMA_SRU_DOMAIN"] = "test-host"
    app.config["ALMA_SRU_INSTITUTION_CODE"] = "test-code"

    ext = InvenioAlma()
    assert "invenio-alma" not in app.extensions

    ext.init_app(app)
    assert "invenio-alma" in app.extensions
