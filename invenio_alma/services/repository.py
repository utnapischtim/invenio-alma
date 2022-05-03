# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma service repository module."""

from .base import BaseService
from .config import RepositoryServiceConfig


class RepositoryService(BaseService):
    """Alma repository base service class."""

    def __init__(self, config, record_service=None):
        """Constructor.

        :param config: A service configuration
        :param record_service: A repository service. Default to current_records_marc21
        """
        self.config = config
        self.record_service = record_service.record_service

    @classmethod
    def build(cls, record_service):
        """Build method."""
        config = RepositoryServiceConfig()
        return cls(config, record_service)

    def _search(self, identity, **kwargs):
        """Search records in the repository.

        :param identity (Identity): Itentity used to authenticate in the repository

        :return dict: hits of repository records.
        """
        results = self.record_service.scan(identity, **kwargs)
        results = results.to_dict()
        return results

    def get_records(self, identity, **kwargs):
        """Search records in the repository.

        :param identity (Identity): Itentity used to authenticate in the repository

        :return []: list of records hit.
        """
        results = self._search(identity, **kwargs)
        records = results.get("hits", {}).get("hits", [])
        return records
