# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Alma Resources configuration."""
from typing import ClassVar

from flask_resources import ResourceConfig, ResponseHandler
from invenio_records_marc21.resources.serializers import (
    Marc21JSONSerializer,
    Marc21XMLSerializer,
)
from invenio_records_marc21.resources.serializers.ui import Marc21UIXMLSerializer
from marshmallow.fields import Field, Str


class AlmaResourceConfig(ResourceConfig):
    """Marc21 Record resource configuration."""

    blueprint_name: str = "alma_records"
    url_prefix: str = "/alma"

    routes: ClassVar[dict[str, str]] = {
        "item": "/<any({types}):type>/<record_id>",
    }

    response_handlers: ClassVar[dict[str, ResponseHandler]] = {
        "application/json": ResponseHandler(Marc21JSONSerializer()),
        "application/marcxml": ResponseHandler(Marc21XMLSerializer()),
        "application/vnd.inveniomarc21.v1+marcxml": ResponseHandler(
            Marc21UIXMLSerializer(),
        ),
    }

    record_id_search_key: ClassVar[dict[str, str]] = {
        "ac_number": "local_control_field_009",
        "mmsid": "mms_id",
    }

    # Request parsing
    request_read_args: ClassVar[dict] = {}
    request_view_args: ClassVar[dict[str]] = {
        "type": Str(),
        "record_id": Field(),
    }
