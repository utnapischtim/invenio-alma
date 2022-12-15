# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma SRU Service."""

from .base import AlmaAPIBase
from .config import AlmaSRUConfig


class AlmaSRUUrls:
    """Alma SRU urls."""

    def __init__(self, config):
        """Constructor for Alma SRU urls."""
        self.config = config
        self.search_value = ""

    @property
    def base_url(self):
        """Base url."""
        return f"https://{self.config.domain}/view/sru/{self.config.institution_code}"

    @property
    def query(self):
        """Query."""
        return f"query=alma.{self.config.search_key}={self.search_value}"

    @property
    def parameters(self):
        """Parameters."""
        return f"version=1.2&operation=searchRetrieve&{self.query}"

    def url(self, search_value):
        """Alma sru url to retrieve record by search value."""
        self.search_value = search_value
        return f"{self.base_url}?{self.parameters}"


class AlmaSRU(AlmaAPIBase):
    """Alma SRU Service class."""

    def __init__(self):
        """Constructor alma sru service."""
        namespaces = {
            "srw": "http://www.loc.gov/zing/srw/",
            "slim": "http://www.loc.gov/MARC21/slim",
        }
        super().__init__(".//srw:recordData/slim:record", namespaces)


class AlmaSRUService:
    """AlmaSRUService."""

    def __init__(self, config, urls, service):
        """Constructor for AlmaService."""
        self.config = config
        self.urls = urls
        self.service = service

    @classmethod
    def build(
        cls, search_key, domain, institution_code, config=None, urls=None, service=None
    ):
        """Build sru service."""
        config = (
            config if config else AlmaSRUConfig(search_key, domain, institution_code)
        )
        urls = urls if urls else AlmaSRUUrls(config)
        service = service if service else AlmaSRU()
        return cls(config, urls, service)

    def get_record(self, ac_number):
        """Get the record."""
        url = self.urls.url(ac_number)
        return self.service.get(url)