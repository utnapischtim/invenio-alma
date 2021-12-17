# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Common utils functions."""

import time
import typing as t
from dataclasses import dataclass
from os.path import basename

import requests
from flask_principal import Identity
from invenio_access import any_user
from invenio_access.utils import get_identity
from invenio_accounts import current_accounts
from invenio_records_marc21 import current_records_marc21
from invenio_records_marc21.services.record.metadata import Marc21Metadata
from invenio_records_marc21.services.services import Marc21RecordFilesService
from lxml import etree


@dataclass(frozen=True)
class AlmaConfig:
    search_key: str
    domain: str
    institution_code: str


@dataclass(frozen=True)
class RecordConfig:
    ac_number: str
    file_: t.IO


def get_identity_from_user_by_email(email: str = None) -> Identity:
    """Get the user specified via email or ID."""
    if email is None:
        raise ValueError("the email has to be set to get a identity")

    user = current_accounts.datastore.get_user(email)

    if user is None:
        raise LookupError(f"user with {email} not found")

    identity = get_identity(user)

    # TODO: this is a temporary solution. this should be done with data from the db
    identity.provides.add(any_user)

    return identity


def get_response_from_alma(alma_config: AlmaConfig, search_value: str) -> etree:
    base_url = f"https://{alma_config.domain}/view/sru/{alma_config.institution_code}"
    parameters = f"version=1.2&operation=searchRetrieve&query=alma.{alma_config.search_key}={search_value}"
    url = f"{base_url}?{parameters}"

    response = requests.get(url)

    return etree.fromstring(response.text.encode("utf-8"))


def get_record(alma_config: AlmaConfig, search_value: str) -> etree:
    alma_response = get_response_from_alma(alma_config, search_value=search_value)

    namespaces = {
        "srw": "http://www.loc.gov/zing/srw/",
        "slim": "http://www.loc.gov/MARC21/slim",
    }
    record = alma_response.find(".//srw:recordData//slim:record", namespaces=namespaces)

    # TODO error handling

    return record


def add_file_to_record(
    marcid: str,
    file_: t.IO,
    file_service: Marc21RecordFilesService,
    identity: Identity,
) -> None:
    filename = basename(file_.name)
    data = [{"key": filename}]

    file_service.init_files(id_=marcid, identity=identity, data=data)
    file_service.set_file_content(
        id_=marcid, file_key=filename, identity=identity, stream=file_
    )
    file_service.commit_file(id_=marcid, file_key=filename, identity=identity)


def create_record(
    alma_config: AlmaConfig,
    record_config: RecordConfig,
    identity: Identity,
):
    """Create the record."""

    marc21_etree = get_record(alma_config, search_value=record_config.ac_number)

    metadata = Marc21Metadata()
    metadata.load(marc21_etree)

    service = current_records_marc21.records_service

    draft = service.create(metadata=metadata, identity=identity, files=True)

    add_file_to_record(
        marcid=draft._record["id"],
        file_=record_config.file_,
        file_service=service.draft_files,
        identity=identity,
    )

    # to prevent the race condition bug.
    # see https://github.com/inveniosoftware/invenio-rdm-records/issues/809
    time.sleep(0.5)

    return service.publish(id_=draft.id, identity=identity)
