# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Alma API Resource."""


from flask import abort
from flask_resources import (
    Resource,
    from_conf,
    request_body_parser,
    request_parser,
    resource_requestctx,
    response_handler,
    route,
)
from invenio_records_marc21 import Marc21Metadata

from ..services.errors import AlmaAPIError  # noqa: TID252
from .config import AlmaResourceConfig

request_view_args = request_parser(from_conf("request_view_args"), location="view_args")
request_read_args = request_parser(from_conf("request_read_args"), location="args")

request_data = request_body_parser(
    parsers=from_conf("request_body_parsers"),
    default_content_type=from_conf("default_content_type"),
)


class AlmaResource(Resource):
    """Bibliographic record resource."""

    config_name = "ALMA_RESOURCES_CONFIG"
    default_config = AlmaResourceConfig

    def __init__(self, service, config=default_config) -> None:  # noqa: ANN001
        """Initialize the alma resource."""
        super().__init__(config=config)
        self.service = service

    def create_url_rules(self) -> list[dict]:
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        types = ",".join(self.config.record_id_search_key.keys())
        rules = [
            route("GET", routes["item"].format(types=types), self.read),
        ]

        return rules

    @request_read_args
    @request_view_args
    @response_handler()
    def read(self) -> dict[dict, int]:
        """Read an item."""
        record_id = resource_requestctx.view_args["record_id"]
        type_id = resource_requestctx.view_args["type"]

        self.service.config.search_key = self.config.record_id_search_key[type_id]
        try:
            metadata = Marc21Metadata(metadata=self.service.get_record(record_id))
            item = metadata.json
        except AlmaAPIError:
            abort(404)
        return item, 200
