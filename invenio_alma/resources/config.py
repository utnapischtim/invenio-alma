# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Alma Resources configuration."""

import marshmallow as ma
from flask_resources import ResourceConfig, ResponseHandler
from invenio_records_marc21.resources.serializers import (
    Marc21JSONSerializer,
    Marc21XMLSerializer,
)
from invenio_records_marc21.resources.serializers.ui import Marc21UIXMLSerializer


class AlmaResourceConfig(ResourceConfig):  # pylint: disable=too-few-public-methods
    """Marc21 Record resource configuration."""

    blueprint_name = "alma_records"
    url_prefix = "/alma"

    routes = {
        "item": "/<any({types}):type>/<record_id>",
    }

    response_handlers = {
        "application/json": ResponseHandler(Marc21JSONSerializer()),
        "application/marcxml": ResponseHandler(Marc21XMLSerializer()),
        "application/vnd.inveniomarc21.v1+marcxml": ResponseHandler(
            Marc21UIXMLSerializer(),
        ),
    }

    record_id_search_key = {
        "ac_number": "local_control_field_009",
        "mmsid": "mms_id",
    }

    # Request parsing
    request_read_args = {}
    request_view_args = {"type": ma.fields.Str(), "record_id": ma.fields.Field()}
