# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the Alma-Connector module."""

import click
import requests
from flask.cli import with_appcontext
from flask_principal import Identity
from invenio_access import any_user
from invenio_records_marc21 import current_records_marc21
from invenio_records_marc21.records.systemfields.access import AccessStatusEnum
from invenio_records_marc21.services.record.metadata import Marc21Metadata
from lxml import etree


def system_identity():
    """System identity."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity


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
def sru(search_key, search_value, domain, institution_code):
    url = f"https://{domain}/view/sru/{institution_code}?version=1.2&operation=searchRetrieve&query=alma.{search_key}={search_value}"
    response = requests.get(url)
    xml = etree.fromstring(response.text.encode("utf-8"))

    namespaces = {
        "srw": "http://www.loc.gov/zing/srw/",
        "slim": "http://www.loc.gov/MARC21/slim",
    }
    record = xml.find(".//srw:recordData//slim:record", namespaces=namespaces)

    metadata = Marc21Metadata()
    metadata.load(record)

    access = {
        "owned_by": [{"user": system_identity().id}],
        "files": AccessStatusEnum.PUBLIC.value,
        "metadata": AccessStatusEnum.PUBLIC.value,
    }

    service = current_records_marc21.records_service
    draft = service.create(metadata=metadata, identity=system_identity(), access=access)
    record = service.publish(id_=draft.id, identity=system_identity())

    print(record.id)
