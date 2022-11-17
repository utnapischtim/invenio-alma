# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils."""

import functools

from invenio_config_tugraz import get_identity_from_user_by_email
from invenio_records_marc21 import current_records_marc21

from .proxies import current_alma


def preliminaries(user_email, *, use_rest=False, use_sru=False):
    """Preliminaries to interact with the repository."""
    records_service = current_records_marc21.records_service
    if use_rest:
        alma_service = current_alma.alma_rest_service
    elif use_sru:
        alma_service = current_alma.alma_sru_service
    else:
        raise RuntimeError("Neither of mms_id and thesis_id were given.")

    identity = get_identity_from_user_by_email(email=user_email)

    return records_service, alma_service, identity


def apply_aggregators(aggregators):
    """Apply aggregators."""
    # pylint: disable=invalid-name
    def fn(accumulator, aggregator):
        return accumulator + aggregator()

    return functools.reduce(fn, aggregators, [])
