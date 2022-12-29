# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""API functions of the alma connector."""

from csv import DictReader
from time import sleep

from flask import current_app
from flask_principal import Identity
from invenio_records_marc21 import (
    DuplicateRecordError,
    Marc21Metadata,
    Marc21RecordService,
    MarcDraftProvider,
    check_about_duplicate,
    convert_json_to_marc21xml,
    create_record,
    current_records_marc21,
)
from invenio_search.engine import dsl
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import StaleDataError

from .services import AlmaRESTError, AlmaRESTService, AlmaSRUService
from .utils import is_duplicate_in_alma


def create_alma_record(
    records_service: Marc21RecordService,
    alma_service: AlmaRESTService,
    identity: Identity,
    marc_id: str,
    cms_id: str,
) -> None:
    """Create a record in alma.

    Normally - depending on the API_KEY - the record will be created in
    the Institution Zone (IZ).
    """
    record = records_service.read_draft(identity, marc_id)
    marc21_record_etree = convert_json_to_marc21xml(json=record.to_dict()["metadata"])

    if is_duplicate_in_alma(cms_id):
        return

    try:
        response = alma_service.create_record(marc21_record_etree)
        current_app.logger.info(response)
    except AlmaRESTError as e:
        current_app.logger.warning(e)


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
        id_=marc_id, identity=identity, metadata=marc21_record_from_alma
    )
    records_service.publish(id_=marc_id, identity=identity)


def import_record(
    alma_service: AlmaSRUService,
    ac_number: str,
    file_path: str,
    identity: Identity,
    marcid: str = None,
    **_,
):
    """Process a single import of a alma record by ac number."""
    if marcid:
        MarcDraftProvider.predefined_pid_value = marcid

    service = current_records_marc21.records_service

    retry_counter = 0
    run = True
    while run:
        try:
            check_about_duplicate(ac_number)

            marc21_record = Marc21Metadata(alma_service.get_record(ac_number))
            record = create_record(service, marc21_record, file_path, identity)

            current_app.logger.info(f"record.id: {record.id}, ac_number: {ac_number}")
            run = False
        except FileNotFoundError:
            current_app.logger.info(f"FileNotFoundError search_value: {ac_number}")
            run = False
        except DuplicateRecordError as error:
            current_app.logger.info(error)
            run = False
        except StaleDataError:
            current_app.logger.info(f"StaleDataError    search_value: {ac_number}")
            run = False
        except ValidationError:
            current_app.logger.info(f"ValidationError   search_value: {ac_number}")
            run = False
        except dsl.RequestError:
            current_app.logger.info(f"RequestError      search_value: {ac_number}")
            run = False
        except dsl.ConnectionTimeout:
            msg = f"ConnectionTimeout search_value: {ac_number}, retry_counter: {retry_counter}"
            current_app.logger.info(msg)

            # cool down the opensearch indexing process. necessary for
            # multiple imports in a short timeframe
            sleep(100)

            # don't overestimate the problem. if three rounds doesn't help go to
            # the next ac number
            if retry_counter > 3:
                run = False
            retry_counter += 1


def import_list_of_records(
    alma_service: AlmaSRUService, csv_file: DictReader, identity: Identity
):
    """Process csv file."""
    for row in csv_file:
        if len(row["ac_number"]) == 0:
            continue

        import_record(alma_service, **row, identity=identity)
