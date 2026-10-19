# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Helper proxy to the state object."""

from typing import cast

from flask import current_app
from werkzeug.local import LocalProxy

from .ext import InvenioAlma

current_alma: InvenioAlma = cast(
    InvenioAlma,
    LocalProxy(lambda: current_app.extensions["invenio-alma"]),
)
"""Helper proxy to get the current alma extension."""
