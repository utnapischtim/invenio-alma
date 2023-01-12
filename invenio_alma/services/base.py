# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma Base Service."""
from xml.etree.ElementTree import Element, fromstring

from requests import get

from .errors import AlmaAPIError


class AlmaAPIBase:
    """Alma remote base service."""

    def __init__(self, xpath_to_records, namespaces=None):
        """Constructor alma api base service."""
        self.xpath_to_records = xpath_to_records
        self.namespaces = namespaces if namespaces else {}

    @property
    def headers(self) -> dict:
        """Headers."""
        return {
            "content-type": "application/xml",
            "accept": "application/xml",
        }

    @staticmethod
    def parse_alma_record(data: str) -> Element:
        """Parse Alma record."""
        data = data.encode("utf-8")

        return fromstring(data)

    def extract_alma_records(self, data: str) -> list[Element]:
        """Extract record from request.

        :param data (str): result list

        :return lxml.Element: extracted record
        """
        record = self.parse_alma_record(data)

        # extract single record
        bibs = record.xpath(self.xpath_to_records, namespaces=self.namespaces)

        if len(bibs) == 0:
            msg = f"xpath: {self.xpath_to_records} does not find records."
            raise AlmaAPIError(code="500", msg=msg)

        return bibs

    def get(self, url: str) -> list[Element]:
        """Alma base api get request.

        :param url (str): url to api

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        response = get(url, headers=self.headers, timeout=10)
        if response.status_code >= 400:
            raise AlmaAPIError(code=response.status_code, msg=response.text)
        return self.extract_alma_records(response.text)
