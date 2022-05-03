# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma service base module."""


class BaseService:  # pylint: disable=too-few-public-methods
    """Alma base record service class."""

    def __init__(self, config):
        """Constructor.

        :param config: A service configuration
        """
        self.config = config
