# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma SRU Service."""
from xml.etree.ElementTree import Element

from .base import AlmaAPIBase
from .config import AlmaSRUConfig


class AlmaSRUUrls:
    """Alma SRU urls."""

    def __init__(self, config: AlmaSRUConfig) -> None:
        """Create object AlmaSRUUrls."""
        self.config = config
        self.search_key = config.search_key
        self.search_value = ""

    @property
    def base_url(self) -> str:
        """Base url."""
        return f"https://{self.config.domain}/view/sru/{self.config.institution_code}"

    @property
    def query(self) -> str:
        """Query."""
        return f"query=alma.{self.search_key}={self.search_value}"

    @property
    def parameters(self) -> str:
        """Parameters."""
        return f"version=1.2&operation=searchRetrieve&{self.query}"

    def url(self, search_value: str, search_key: str = None) -> str:
        """Alma sru url to retrieve record by search value."""
        self.search_value = search_value
        if search_key:
            self.search_key = search_key
        return f"{self.base_url}?{self.parameters}"


class AlmaSRU(AlmaAPIBase):
    """Alma SRU Service class."""

    def __init__(self) -> None:
        """Create object AlmaSRU."""
        namespaces = {
            "srw": "http://www.loc.gov/zing/srw/",
            "slim": "http://www.loc.gov/MARC21/slim",
        }
        super().__init__(".//srw:recordData/slim:record", namespaces)


class AlmaSRUService:
    """AlmaSRUService."""

    def __init__(
        self,
        config: AlmaSRUConfig,
        urls: AlmaSRUUrls,
        service: AlmaSRU,
    ) -> None:
        """Create object AlmaSRUService."""
        self.config = config
        self.urls = urls
        self.service = service

    @classmethod
    def build(  # noqa: ANN206
        cls,
        config: AlmaSRUConfig,
    ):
        """Build sru service."""
        urls = AlmaSRUUrls(config)
        service = AlmaSRU()
        return cls(config, urls, service)

    def get_record(self, ac_number: str, search_key: str = None) -> list[Element]:
        """Get the record."""
        url = self.urls.url(ac_number, search_key)
        return self.service.get(url)
