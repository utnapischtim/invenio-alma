# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma Service config class."""
from dataclasses import dataclass


@dataclass
class AlmaServiceConfig:
    """Alma service configuration class."""

    api_host = ""
    api_key = ""
    # TODO: check if ind1 and ind2 has to be checked or not
    url_xpath = (
        ".//datafield[@ind1='4' and @ind2=' ' and @tag='856']/subfield[@code='u']"
    )

    def __init__(self, api_key, api_host):
        """Constructor for the Alma service config."""
        self.api_key = api_key
        self.api_host = api_host


@dataclass
class RepositoryServiceConfig:
    """Repository service configuration class."""

    mms_id_path = "metadata.fields.001"
    ac_id_path = "metadata.fields.009"
    rec_id_path = "id"
