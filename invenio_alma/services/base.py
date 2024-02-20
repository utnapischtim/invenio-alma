# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma Base Service."""

from __future__ import annotations

from http import HTTPStatus
from xml.etree.ElementTree import Element, fromstring

from requests import ReadTimeout, get

from .errors import AlmaAPIError


class AlmaAPIBase:
    """Alma remote base service."""

    def __init__(self, xpath_to_records: str, namespaces: str | None = None) -> None:
        """Create alma api base service."""
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

        return fromstring(data)  # noqa: S314

    def extract_alma_records(self, data: str) -> list[Element]:
        """Extract record from request.

        :param data (str): result list

        :return lxml.Element: extracted record
        """
        record = self.parse_alma_record(data)

        # extract single record
        bibs = list(record.iterfind(self.xpath_to_records, namespaces=self.namespaces))

        if len(bibs) == 0:
            msg = f"xpath: {self.xpath_to_records} does not find records."
            raise AlmaAPIError(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=msg)

        return bibs

    def get(self, url: str) -> list[Element]:
        """Alma base api get request.

        :param url (str): url to api

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        try:
            response = get(url, headers=self.headers, timeout=10)
        except ReadTimeout as exc:
            raise AlmaAPIError(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                msg="readtimeout",
            ) from exc

        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise AlmaAPIError(code=response.status_code, msg=response.text)

        return self.extract_alma_records(response.text)
