# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma Service."""

import requests
from lxml.etree import fromstring, tostring

from .config import AlmaServiceConfig
from .errors import AlmaAPIError, AlmaRESTError, AlmaSRUError


class AlmaRESTUrls:
    """Alma REST urls."""

    def __init__(self, config):
        """Constructor Alma REST Urls."""
        self.config = config

    @property
    def base_url(self):
        """Base url."""
        return f"https://{self.config.api_host}/almaws/v1/bibs"

    def url_get(self, mms_id):
        """Alma rest api get record url.

        :param mms_id (str): alma record id

        :return str: alma api url.
        """
        return f"{self.config.base_url}?mms_id={mms_id}&apikey={self.config.api_key}"

    def url_put(self, mms_id):
        """Alma rest api put record url.

        :param mms_id (str): alma record id

        :return str: alma api url.
        """
        return f"{self.config.base_url}?{mms_id}?apikey={self.config.api_key}"


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


class AlmaAPIBaseService:
    """Alma remote base service."""

    def __init__(self, xpath_to_records, namespaces=None):
        """Constructor alma api base service."""
        self.xpath_to_records = xpath_to_records
        self.namespaces = namespaces if namespaces else {}

    @property
    def headers(self):
        """Headers."""
        return {
            "content-type": "application/xml",
            "accept": "application/xml",
        }

    @staticmethod
    def parse_alma_record(self, data):
        """Parse Alma record."""
        data = data.encode("utf-8")

        return fromstring(data)

    def extract_alma_records(self, data):
        """Extract record from request.

        :param data (str): result list

        :return lxml.Element: extracted record
        """

        record = self.parse_alma_record

        # extract single record
        bibs = record.xpath(self.xpath_to_records, namespaces=self.namespaces)

        if len(bibs) == 0:
            msg = f"xpath: {self.xpath_to_records} does not find records."
            raise AlmaAPIError(msg=msg)

        return bibs


class AlmaRESTService(AlmaAPIBaseService):
    """Alma REST service class."""

    def __init__(self):
        """Constructor alma rest service."""
        super().__init__(".//bib/record")

    def get(self, url):
        """Alma rest api get request.

        :param url (str): url to api

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        response = requests.get(url, headers=self.headers)
        if response.status_code >= 400:
            raise AlmaRESTError(code=response.status_code, msg=response.text)
        return self.extract_alma_records(response.text)

    def put(self, url, data):
        """Alma rest api put request.

        :param url (str): url to api
        :param data (str): payload

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        response = requests.put(url, data, headers=self.headers)
        if response.status_code >= 400:
            raise AlmaRESTError(code=response.status_code, msg=response.text)
        return response.text


class AlmaSRUService(AlmaAPIBaseService):
    """Alma SRU Service class."""

    def __init__(self):
        """Constructor alma sru service."""
        namespaces = {
            "srw": "http://www.loc.gov/zing/srw/",
            "slim": "http://www.loc.gov/MARC21/slim",
        }
        super().__init__(".//srw:recordData/slim:record", namespaces)

    def sru(self, url):
        """Alma sru service get record."""
        response = requests.get(url, headers=self.headers)
        if response.status_code >= 400:
            raise AlmaSRUError(code=response.status_code, msg=response.text)
        return response.text


class AlmaService:
    """Alma service class."""

    def __init__(self, config, rest_urls, rest_service):
        """Constructor for AlmaService."""
        self.config = config
        self.rest_urls = rest_urls
        self.rest_service = rest_service

    @classmethod
    def build(cls, api_key, api_host):
        """Build method."""
        config = AlmaServiceConfig(api_key, api_host)
        rest_urls = AlmaRESTUrls(config)
        rest_service = AlmaRESTService()
        return cls(config, rest_urls, rest_service)

    def update_url(self, mms_id, new_url):
        """Change url in a record.

        :param records ([Dict]): List of repository records
        :params new_url (str): new repository url. Url must contain '{recid}'
        """
        # prepare record
        api_url = self.rest_urls.url_get(mms_id)
        records = self.rest_service.get(api_url)

        # extract url subfield
        url_datafield = metadata.xpath(self.config.url_xpath)

        if len(url_datafield) == 0:
            # No URL subfield in a record
            # TODO: create new datafield
            return

        url_datafield = url_datafield[0]
        url_datafield.text = new_url
        alma_record = tostring(metadata)
        alma_record = alma_record.decode("UTF-8")
        url_put = self.rest_urls.url_put(mms_id)

        self.rest_service.put(url_put, alma_record)
