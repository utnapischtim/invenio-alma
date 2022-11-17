# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""API functions of the alma connector."""

from time import sleep

from invenio_records_marc21 import (
    DuplicateRecordError,
    Marc21Metadata,
    MarcDraftProvider,
    check_about_duplicate,
    create_record,
    current_records_marc21,
)
from invenio_search.engine import dsl
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import StaleDataError


def create_alma_record(records_service, alma_service, identity, marc_id):
    """Create alma record."""
    record = records_service.read(identity, marc_id)
    marc21_record = Marc21Metadata(json=record.to_dict()["metadata"])
    # pylint: disable=unused-variable
    response = alma_service.create_record(marc21_record.etree)

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


# pylint: disable-next=too-many-return-statements)
def import_record(alma_sru_service, ac_number, file_path, identity, marcid=None, **_):
    """Process a single import of a alma record by ac number."""
    if marcid:
        MarcDraftProvider.predefined_pid_value = marcid

    service = current_records_marc21.records_service

    retry_counter = 0
    while True:
        try:
            check_about_duplicate(ac_number)

            marc21_record = Marc21Metadata(alma_sru_service.get_record(ac_number))
            record = create_record(service, marc21_record, file_path, identity)

            print(f"record.id: {record.id}, ac_number: {ac_number}")
            return
        except FileNotFoundError:
            print(f"FileNotFoundError search_value: {ac_number}")
            return
        except DuplicateRecordError as error:
            print(error)
            return
        except StaleDataError:
            print(f"StaleDataError    search_value: {ac_number}")
            return
        except ValidationError:
            print(f"ValidationError   search_value: {ac_number}")
            return
        except dsl.RequestError:
            print(f"RequestError      search_value: {ac_number}")
            return
        except dsl.ConnectionTimeout:
            msg = f"ConnectionTimeout search_value: {ac_number}, retry_counter: {retry_counter}"
            print(msg)

            # cool down the elasticsearch indexing process. necessary for
            # multiple imports in a short timeframe
            sleep(100)

            # don't overestimate the problem. if three rounds doesn't help go to
            # the next ac number
            if retry_counter > 3:
                return
            retry_counter += 1


def import_list_of_records(alma_sru_service, csv_file, identity):
    """Process csv file."""
    for row in csv_file:
        if len(row["ac_number"]) == 0:
            continue

        import_record(alma_sru_service, **row, identity=identity)
