# SPDX-FileCopyrightText: 2023-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alma Resources configuration."""

from types import MappingProxyType

from flask_resources import ResourceConfig, ResponseHandler
from flask_resources.serializers import JSONSerializer
from marshmallow.fields import Raw, Str


class AlmaResourceConfig(ResourceConfig):
    """Marc21 Record resource configuration."""

    blueprint_name: str = "alma_records"
    url_prefix: str = "/alma"

    routes = MappingProxyType(
        {
            "item": "/<any({types}):type>/<record_id>",
        },
    )

    response_handlers = MappingProxyType(
        {
            "application/json": ResponseHandler(JSONSerializer()),
        },
    )

    record_id_search_key = MappingProxyType(
        {
            "ac_number": "local_control_field_009",
            "mmsid": "mms_id",
        },
    )

    # Request parsing
    request_read_args = MappingProxyType({})
    request_view_args = MappingProxyType(
        {
            "type": Str(),
            "record_id": Raw(),
        },
    )
