# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""API functions of the alma connector."""

from __future__ import annotations

from time import sleep

from flask import current_app
from flask_principal import Identity
from invenio_access.permissions import system_process
from invenio_records_marc21 import (
    DuplicateRecordError,
    Marc21Metadata,
    Marc21RecordService,
    MarcDraftProvider,
    check_about_duplicate,
    convert_json_to_marc21xml,
    create_record,
)
from invenio_records_marc21.services.record.types import ACNumber
from invenio_search.engine import search
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import StaleDataError

from .services import AlmaRESTError, AlmaRESTService, AlmaSRUService
from .types import Color
from .utils import is_duplicate_in_alma

MAX_RETRY_COUNT = 3
"""There could be problems with opensearch connections. This is the retry counter."""


def create_alma_record(
    records_service: Marc21RecordService,
    alma_service: AlmaRESTService,
    identity: Identity,
    marc_id: str,
    cms_id: str = "",
) -> None:
    """Create a record in alma.

    Normally - depending on the API_KEY - the record will be created in
    the Institution Zone (IZ).
    """
    identity.provides.add(system_process)
    record = records_service.read_draft(identity, marc_id)
    marc21_record_etree = convert_json_to_marc21xml(record.to_dict()["metadata"])

    if is_duplicate_in_alma(cms_id):
        return

    try:
        response = alma_service.create_record(marc21_record_etree)
        current_app.logger.info(response)
    except AlmaRESTError as rest_error:
        current_app.logger.warning(rest_error)
        raise


def update_repository_record(
    records_service: Marc21RecordService,
    alma_service: AlmaSRUService,
    marc_id: str,
    identity: Identity,
    alma_thesis_id: str,
) -> None:
    """Update repository record fetched from alma."""
    marc21_etree = alma_service.get_record(alma_thesis_id)
    marc21_record_from_alma = Marc21Metadata(metadata=marc21_etree)

    records_service.edit(id_=marc_id, identity=identity)
    records_service.update_draft(
        id_=marc_id,
        identity=identity,
        metadata=marc21_record_from_alma,
    )
    records_service.publish(id_=marc_id, identity=identity)


def import_record(
    records_service: Marc21RecordService,
    alma_service: AlmaSRUService,
    ac_number: str,
    file_path: str,
    identity: Identity,
    access: str,
    marcid: str | None = None,
    **_: any,
) -> None:
    """Process a single import of a alma record by ac number."""
    if marcid:
        MarcDraftProvider.predefined_pid_value = marcid

    retry_counter = 0
    while True:
        try:
            check_about_duplicate(ACNumber(ac_number))

            metadata = alma_service.get_record(ac_number)[0]
            marc21_record = Marc21Metadata(metadata=metadata)

            data = marc21_record.json
            data["access"] = {
                "record": "public",
                "files": "public" if access == "public" else "restricted",
            }

            record = create_record(records_service, data, [file_path], identity)
            return {
                "msg": f"record.id: {record.id}, ac_number: {ac_number}",
                "color": Color.success,
            }
        except FileNotFoundError:
            return {
                "msg": f"FileNotFoundError search_value: {ac_number}, file_path: {file_path}",  # noqa: E501
                "color": Color.error,
            }
        except DuplicateRecordError as error:
            return {
                "msg": str(error),
                "color": Color.error,
            }
        except StaleDataError:
            return {
                "msg": f"StaleDataError    search_value: {ac_number}",
                "color": Color.error,
            }
        except ValidationError as error:
            return {
                "msg": f"ValidationError   search_value: {ac_number}, error: {error}",
                "color": Color.error,
            }
        except search.RequestError:
            return {
                "msg": f"RequestError      search_value: {ac_number}",
                "color": Color.error,
            }
        except search.ConnectionTimeout:
            # cool down the opensearch indexing process. necessary for
            # multiple imports in a short timeframe
            sleep(100)

            if retry_counter > MAX_RETRY_COUNT:
                msg = f"ConnectionTimeout search_value: {ac_number}, retry_counter: {retry_counter}"  # noqa: E501
                return {"msg": msg, "color": Color.error}

            retry_counter += 1
