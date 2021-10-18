# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the Alma-Connector module."""

from os.path import basename
from pprint import pprint

import click
import requests
from flask.cli import with_appcontext
from flask_principal import Identity
from invenio_access import any_user
from invenio_access.utils import get_identity
from invenio_accounts import current_accounts
from invenio_records_marc21 import current_records_marc21
from invenio_records_marc21.records import Marc21Record
from invenio_records_marc21.records.systemfields.access import AccessStatusEnum
from invenio_records_marc21.services.record.metadata import Marc21Metadata
from lxml import etree


def system_identity():
    """System identity."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity


def get_user_by_identifier(id_or_email):
    """Get the user specified via email or ID."""
    if id_or_email is None:
        raise ValueError("id_or_email cannot be None")

    # note: this seems like the canonical way to go
    #       'id_or_email' can be either an integer (id) or email address
    user = current_accounts.datastore.get_user(id_or_email)
    pprint(user)
    if user is None:
        raise LookupError("user not found: %s" % id_or_email)

    return user


def get_identity_for_user(user):
    """Get the Identity for the user specified via email or ID."""
    if user is None:
        return system_identity()

    found_user = get_user_by_identifier(user)
    identity = get_identity(found_user)
    print("get_identity_for_user")
    pprint(identity)
    identity.provides.add(any_user)
    pprint(identity)
    return identity


def get_response_from_alma(
    search_key: str, search_value: str, domain: str, institution_code: str
) -> etree:
    url = f"https://{domain}/view/sru/{institution_code}?version=1.2&operation=searchRetrieve&query=alma.{search_key}={search_value}"
    response = requests.get(url)
    return etree.fromstring(response.text.encode("utf-8"))


def get_record(alma_response: etree) -> etree:
    namespaces = {
        "srw": "http://www.loc.gov/zing/srw/",
        "slim": "http://www.loc.gov/MARC21/slim",
    }
    record = alma_response.find(".//srw:recordData//slim:record", namespaces=namespaces)

    # TODO error handling

    return record


def create_access():
    return {
        "owned_by": [{"user": system_identity().id}],
        "files": AccessStatusEnum.PUBLIC.value,
        "metadata": AccessStatusEnum.PUBLIC.value,
    }


def add_file(file_service, draft, file_, identity):
    draft.files.enable = True
    draft.commit()

    recid = draft["id"]
    filename = basename(file_.name)

    file_service.init_files(id_=recid, identity=identity, data=[{"key": filename}])
    file_service.set_file_content(
        id_=recid, file_key=filename, identity=identity, stream=file_
    )
    file_service.commit_file(id_=recid, file_key=filename, identity=identity)


@click.group()
def alma():
    """Alma CLI."""


@alma.command()
@click.option("--mms-id", type=click.STRING, required=True)
def show(mms_id):
    pass


@alma.command()
@with_appcontext
@click.option("--search-key", type=click.STRING, required=True)
@click.option("--search-value", type=click.STRING, required=True)
@click.option("--domain", type=click.STRING, required=True)
@click.option("--institution-code", type=click.STRING, required=True)
@click.option("--file", "file_", type=click.File("rb"), required=False)
@click.option("--user", type=click.STRING, default="alma@tugraz.at")
def sru(search_key, search_value, domain, institution_code, file_, user):
    response = get_response_from_alma(
        search_key, search_value, domain, institution_code
    )
    record = get_record(response)

    metadata = Marc21Metadata()
    metadata.load(record)

    access = create_access()
    # identity = get_identity_for_user(user)
    identity = system_identity()
    print("alma sru identity")
    pprint(identity)
    service = current_records_marc21.records_service
    draft = service.create(metadata=metadata, identity=identity, access=access)
    print(f"draft.id:  {draft.id}")

    add_file(service.draft_files, draft._record, file_, identity)

    record = service.publish(id_=draft.id, identity=system_identity())

    print(f"record.id: {record.id}")


@alma.command()
@with_appcontext
def file_upload(ac, marcid, filename):
    pass
