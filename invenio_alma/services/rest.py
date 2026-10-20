# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alma REST Service."""

from http import HTTPStatus
from xml.etree.ElementTree import Element, tostring

from requests.api import post, put
from requests.exceptions import ReadTimeout

from .base import AlmaAPIBase, AlmaService
from .config import AlmaRESTConfig
from .errors import AlmaRESTError


class AlmaRESTUrls:
    """Alma REST urls."""

    def __init__(self, config: AlmaRESTConfig) -> None:
        """Create object AlmaRESTUrls."""
        self.config = config

    @property
    def base_url(self) -> str:
        """Base url."""
        return f"{self.config.api_host}/almaws/v1/bibs"

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

    def __init__(self, timeout: int = 30) -> None:
        """Create object AlmaREST."""
        super().__init__(".//bib/record")
        self.timeout = timeout

    def put(self, url: str, record: Element) -> str:
        """Alma rest api put request.

        :param url (str): url to api
        :param data (str): payload

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        data = tostring(record)

        try:
            response = put(url, data, headers=self.headers, timeout=self.timeout)
        except ReadTimeout as exc:
            raise AlmaRESTError(code=500, msg="readtimeout") from exc

        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise AlmaRESTError(code=response.status_code, msg=response.text)
        return response.text

    def post(self, url: str, record: Element) -> str:
        """Alma rest api post request.

        :param url (str): url to api_host
        :param data (str): payload

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        data = tostring(record)

        try:
            response = post(url, data, headers=self.headers, timeout=self.timeout)
        except ReadTimeout as exc:
            raise AlmaRESTError(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                msg="readtimeout",
            ) from exc

        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise AlmaRESTError(code=response.status_code, msg=response.text)

        return response.text


class AlmaRESTService(AlmaService):
    """Alma service class."""

    def __init__(
        self,
        config: AlmaRESTConfig,
        urls: AlmaRESTUrls | None = None,
        service: AlmaREST | None = None,
    ) -> None:
        """Create object from AlmaRESTService."""
        self.config = config
        self.urls = urls or AlmaRESTUrls(config)
        self.service = service or AlmaREST(self.config.timeout)

    def get_record(self, mms_id: str) -> list[Element]:
        """Get Record from alma."""
        api_url = self.urls.url_get(mms_id)
        return self.service.get(api_url)  # return etree

    def create_record(self, record: Element) -> str:
        """Create record in Alma."""
        bib = Element("bib")
        bib.append(record)

        url_post = self.urls.url_post()
        return self.service.post(url_post, bib)
