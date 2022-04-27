# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma service repository module."""

from invenio_records_marc21.proxies import current_records_marc21

from .base import BaseService


class RepositoryService(BaseService):
    """Alma repository base service class."""

    def __init__(self, config, record_service=None):
        """Constructor.

        :param config: A service configuration
        :param record_service: A repository service. Default to current_records_marc21
        """
        super().__init__(config)
        self._record_module = (
            record_service if record_service else current_records_marc21
        )

    @property
    def _record_service(self):
        """Marc21 repository records service."""
        return self._record_module.records_service

    def _search(self, identity, **kwargs):
        """Search records in the repository.

        :param identity (Identity): Itentity used to authenticate in the repository

        :return dict: hits of repository records.
        """
        results = self._record_service.scan(identity, **kwargs)
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
