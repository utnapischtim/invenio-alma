# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Test Alma Services."""

from invenio_alma.services.rest import AlmaRESTConfig, AlmaRESTUrls
from invenio_alma.services.sru import AlmaSRUConfig, AlmaSRUUrls


def test_alma_rest_urls() -> None:
    """Test rest urls."""
    mms_id = "12345-12345"
    api_key = "api_key"
    api_host = "https://api_host"
    config = AlmaRESTConfig(api_key, api_host)
    urls = AlmaRESTUrls(config)

    expected = f"{api_host}/almaws/v1/bibs?mms_id={mms_id}&apikey={api_key}"
    assert urls.url_get(mms_id) == expected

    expected = f"{api_host}/almaws/v1/bibs/{mms_id}?apikey={api_key}"
    assert urls.url_put(mms_id) == expected


def test_alma_sru_urls() -> None:
    """Test sru urls."""
    search_key = ""
    domain = ""
    institution_code = ""
    search_value = ""
    config = AlmaSRUConfig(search_key, domain, institution_code)
    urls = AlmaSRUUrls(config)

    expected_query = f"query=alma.{search_key}={search_value}"
    expected_parameters = f"version=1.2&operation=searchRetrieve&{expected_query}"
    expected = f"{domain}/view/sru/{institution_code}?{expected_parameters}"
    assert urls.url(search_value) == expected
