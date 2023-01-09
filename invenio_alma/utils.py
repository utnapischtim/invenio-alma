# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils."""

import functools
from typing import Callable, List

from flask import current_app
from invenio_config_tugraz import get_identity_from_user_by_email
from invenio_records_marc21 import current_records_marc21

from .proxies import current_alma
from .services.sru import AlmaSRUService


def is_duplicate_in_alma(cms_id: str):
    """Check if there is already a record in alma."""
    search_key = "local_field_995"
    domain = current_app.config["ALMA_SRU_DOMAIN"]
    institution_code = current_app.config["ALMA_SRU_INSTITUTION_CODE"]
    sru_service = AlmaSRUService(search_key, domain, institution_code)

    record = sru_service.get_record(cms_id)
    return len(record.getchildren()) > 0


def preliminaries(user_email: str, *, use_rest=False, use_sru=False):
    """Preliminaries to interact with the repository."""
    records_service = current_records_marc21.records_service
    if use_rest:
        alma_service = current_alma.alma_rest_service
    elif use_sru:
        search_key = "local_field_995"
        domain = current_app.config["ALMA_SRU_DOMAIN"]
        institution_code = current_app.config["ALMA_SRU_INSTITUTION_CODE"]
        alma_service = AlmaSRUService(search_key, domain, institution_code)
    else:
        raise RuntimeError("choose between using rest or sru.")

    identity = get_identity_from_user_by_email(email=user_email)

    return records_service, alma_service, identity


def apply_aggregators(aggregators: List[Callable[[], list]]) -> list:
    """Apply aggregators."""

    def func(accumulator, aggregator):
        return accumulator + aggregator()

    return functools.reduce(func, aggregators, [])
