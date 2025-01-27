# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma Base Service decorator."""

from collections.abc import Callable
from functools import wraps
from typing import TypedDict, Unpack

from invenio_access.utils import get_identity
from invenio_accounts import current_accounts

from .services import AlmaRESTService, AlmaSRUService
from .services.config import AlmaRESTConfig, AlmaSRUConfig


class KwargsDict(TypedDict, total=False):
    """Kwargs dict."""

    user_email: str
    api_key: str
    api_host: str
    metadata: dict
    search_key: str
    domain: str
    institution_code: str
    ac_number: str
    filename: str
    access: str
    csv_file: dict


def build_service[T](func: Callable[..., T]) -> Callable:
    """Decorate to build the services."""

    @wraps(func)
    def build(*_: dict, **kwargs: Unpack[KwargsDict]) -> T:
        if "api_key" in kwargs and "api_host" in kwargs:
            api_key = kwargs.pop("api_key")
            api_host = kwargs.pop("api_host")

            config = AlmaRESTConfig(api_key, api_host)
            alma_service = AlmaRESTService(config=config)
        elif "search_key" in kwargs and "domain" in kwargs:
            search_key = kwargs.pop("search_key")
            domain = kwargs.pop("domain")
            institution_code = kwargs.pop("institution_code")
            config = AlmaSRUConfig(search_key, domain, institution_code)
            alma_service = AlmaSRUService(config)
        else:
            raise RuntimeError("either rest nor sru configuration given")

        kwargs["alma_service"] = alma_service

        return func(**kwargs)

    return build


def build_identity[T](func: Callable[..., T]) -> Callable:
    """Decorate to build the user."""

    @wraps(func)
    def build(*_: dict, **kwargs: Unpack[KwargsDict]) -> T:
        user = current_accounts.datastore.get_user_by_email(kwargs["user_email"])
        identity = get_identity(user)

        kwargs["identity"] = identity
        del kwargs["user_email"]

        return func(**kwargs)

    return build
