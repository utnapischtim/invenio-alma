# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils."""
from invenio_config_tugraz import get_identity_from_user_by_email
from invenio_records_marc21 import Marc21Metadata, current_records_marc21

from .proxies import current_alma


def create_alma_record(records_service, alma_service, identity, marc_id):
    """Create alma record."""

    record = records_service.read(identity, marc_id)
    marc21_record = Marc21Metadata(json=record.to_dict()["metadata"])
    marc21_xml = alma_service.create_record(marc21_record.etree)

    # TODO: check about errors!


def update_repository_record(
    records_service, alma_service, marc_id, identity, alma_thesis_id
):
    """Update repository record fetched from alma."""

    marc21_etree = alma_service.get_record(alma_thesis_id)
    marc21_record_from_alma = Marc21Metadata(metadata=marc21_etree)

    records_service.edit(id_=marc_id, identity=identity)
    records_service.update_draft(
        id_=marc_id, identity=identity, metadata=marc21_record_from_alma
    )
    records_service.publish(id_=marc_id, identity=identity)


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


def calculate_to_create_alma_records(aggregators):
    """Use the aggregators to calculate the records which should be created in alma."""
    ids = []
    # TODO
    # for aggregator in aggregators:
    #     ids += aggregator()

    return ids


def calculate_to_update_repository_records(aggregators):
    """Use the aggregators to calculate the records which should be updated in repository."""
    ids = []
    # TODO
    # for aggregator in aggregators:
    #     ids += aggregator()

    return ids
