# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio service to connect InvenioRDM to Alma."""

from .alma import AlmaService
from .config import AlmaServiceConfig
from .repository import RepositoryService

__all__ = (
    "AlmaServiceConfig",
    "AlmaService",
    "RepositoryService",
)
