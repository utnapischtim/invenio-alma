# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma REST Service."""
from typing import List
from xml.etree.ElementTree import Element, tostring

from requests import post, put

from .base import AlmaAPIBase
from .config import AlmaRESTConfig
from .errors import AlmaRESTError
from .utils import jpath_to_xpath


class AlmaRESTUrls:
    """Alma REST urls."""

    def __init__(self, config: AlmaRESTConfig):
        """Constructor Alma REST Urls."""
        self.config = config

    @property
    def base_url(self) -> str:
        """Base url."""
        return f"https://{self.config.api_host}/almaws/v1/bibs"

    def url_get(self, mms_id: str) -> str:
        """Alma rest api get record url.

        :param mms_id (str): alma record id

        :return str: alma api url.
        """
        return f"{self.base_url}?mms_id={mms_id}&apikey={self.config.api_key}"

    def url_put(self, mms_id: str) -> str:
        """Alma rest api put record url.

        :param mms_id (str): alma record id

        :return str: alma api url.
        """
        return f"{self.base_url}/{mms_id}?apikey={self.config.api_key}"

    def url_post(self) -> str:
        """Alma rest api post record url.

        :return str: alma api url.
        """
        return f"{self.base_url}?apikey={self.config.api_key}"


class AlmaREST(AlmaAPIBase):
    """Alma REST service class."""

    def __init__(self):
        """Constructor alma rest service."""
        super().__init__(".//bib/record")

    def put(self, url: str, data: str):
        """Alma rest api put request.

        :param url (str): url to api
        :param data (str): payload

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        response = put(url, data, headers=self.headers, timeout=10)
        if response.status_code >= 400:
            raise AlmaRESTError(code=response.status_code, msg=response.text)
        return response.text

    def post(self, url: str, data: str):
        """Alma rest api post request.

        :param url (str): url to api_host
        :param data (str): payload

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        response = post(url, data, headers=self.headers, timeout=10)
        if response.status_code >= 400:
            raise AlmaRESTError(code=response.status_code, msg=response.text)
        return response.text


class AlmaRESTService:
    """Alma service class."""

    def __init__(self, config: AlmaRESTConfig, urls: AlmaRESTUrls, service: AlmaREST):
        """Constructor for AlmaService."""
        self.config = config
        self.urls = urls
        self.service = service

    @classmethod
    def build(
        cls,
        api_key: str,
        api_host: str,
        config: AlmaRESTConfig = None,
        urls: AlmaRESTUrls = None,
        service: AlmaREST = None,
    ):  # -> Self >=python3.11 necessary
        """Build method."""
        config = config if config else AlmaRESTConfig(api_key, api_host)
        urls = urls if urls else AlmaRESTUrls(config)
        service = service if service else AlmaREST()
        return cls(config, urls, service)

    def get_record(self, mms_id: str) -> List[Element]:
        """Get Record from alma."""
        api_url = self.urls.url_get(mms_id)
        return self.service.get(api_url)  # return etree

    @staticmethod
    # pylint: disable-next=unused-argument
    def get_field(
        record: Element,
        field_json_path: str,
        subfield_value: str = "",  # pylint: disable=unused-argument
    ) -> Element:
        """Get field by json path and subfield value if it is set."""
        xpath = jpath_to_xpath(field_json_path)
        field = record.xpath(xpath)

        # TODO check about multiple results
        # allowed only one field, otherwise we have a problem and should sys.exit()

        return field

    @staticmethod
    # pylint: disable-next=unused-argument
    def replace_field(
        field: Element,
        new_subfield_value: str,
        new_subfield_template: str = "",  # pylint: disable=unused-argument
    ) -> None:
        """Replace in-inplace the subfield value with the new subfield value.

        Replace also the metametadata of the field if the template is set.
        """
        # TODO: implement new_subfield_template != ""

        field.text = new_subfield_value

    def update_alma_record(self, mms_id: str, record: Element) -> str:
        """Update the record on alma side."""
        data = tostring(record)  # TODO check if .decode("UTF-8") is necessary
        url_put = self.urls.url_put(mms_id)
        self.service.put(url_put, data)

    def create_alma_record(self, record: Element) -> str:
        """Create alma record."""
        bib = Element("bib")
        bib.append(record)

        data = tostring(bib)
        url_post = self.urls.url_post()
        return self.service.post(url_post, data)

    def update_field(
        self,
        mms_id: str,
        field_json_path: str,
        new_subfield_value: str,
        subfield_value: str = "",
        new_subfield_template: str = "",
    ) -> str:
        """Update field."""
        record = self.get_record(mms_id)
        field = self.get_field(record, field_json_path, subfield_value)  # reference
        self.replace_field(field, new_subfield_value, new_subfield_template)  # in-place
        self.update_alma_record(mms_id, record)

    def create_record(self, record: Element) -> str:
        """Create record in Alma."""
        return self.create_alma_record(record)
