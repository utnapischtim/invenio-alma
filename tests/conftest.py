# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from collections.abc import Callable

import pytest
from _pytest.fixtures import FixtureFunctionMarker
from invenio_app.factory import create_api as _create_api


@pytest.fixture(scope="module")
def app_config(app_config: FixtureFunctionMarker) -> FixtureFunctionMarker:
    """Application config."""
    app_config["ALMA_API_KEY"] = "test-token"
    app_config["ALMA_API_HOST"] = "test-host"
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path: FixtureFunctionMarker) -> Callable:
    """Application factory fixture."""
    return _create_api
