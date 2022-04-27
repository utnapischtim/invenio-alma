# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma Service config class."""


class AlmaServiceConfig:
    """Alma service configuration class."""

    api_host = ""
    api_key = ""
    mms_id_path = "metadata.fields.001"
    ac_id_path = "metadata.fields.009"
    rec_id_path = "id"
    url_path = (
        ".//record//datafield[@ind1='4' and @ind2=' ' "
        "and @tag='856']//subfield[@code='u']"
    )

    @classmethod
    def build(cls, app):
        """Update configuration from flask app."""
        cls.api_key = app.config.get("INVENIO_ALMA_API_KEY", "")
        cls.api_host = app.config.get("INVENIO_ALMA_API_HOST", "")
        return cls

    @classmethod
    def _base_url(cls):
        """Property get base url for alma rest api."""
        return f"https://{cls.api_host}/almaws/v1/bibs"

    @classmethod
    def url_get(cls, mms_id):
        """Alma rest api get record url.

        :param mms_id (str): alma record id

        :return str: alma api url.
        """
        api_url = (
            cls._base_url()
            + f"?mms_id={mms_id}&apikey={cls.api_key}&view=full&expand=None"
        )
        return api_url

    @classmethod
    def url_put(cls, mms_id):
        """Alma rest api put record url.

        :param mms_id (str): alma record id

        :return str: alma api url.
        """
        api_url = cls._base_url() + f"/{mms_id}?apikey={cls.api_key}"
        return api_url
