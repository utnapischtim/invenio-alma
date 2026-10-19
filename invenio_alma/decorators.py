# SPDX-FileCopyrightText: 2025-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alma Base Service decorator."""

from collections.abc import Callable
from functools import wraps
from typing import TypedDict, Unpack

from flask_principal import Identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_accounts

from .services import AlmaRESTService, AlmaSRUService
from .services.base import AlmaService
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
    alma_service: AlmaService
    identity: Identity


def build_service[T](func: Callable[..., T]) -> Callable:
    """Decorate to build the services."""

    @wraps(func)
    def build(*_: dict, **kwargs: Unpack[KwargsDict]) -> T:
        if "api_key" in kwargs and "api_host" in kwargs:
            api_key = kwargs.pop("api_key")
            api_host = kwargs.pop("api_host")

            config_rest = AlmaRESTConfig(api_key, api_host)
            kwargs["alma_service"] = AlmaRESTService(config=config_rest)
        elif "search_key" in kwargs and "domain" in kwargs:
            search_key: str = kwargs.pop("search_key")
            domain: str = kwargs.pop("domain")
            institution_code: str = kwargs.pop("institution_code")
            config_sru = AlmaSRUConfig(search_key, domain, institution_code)
            kwargs["alma_service"] = AlmaSRUService(config=config_sru)
        else:
            msg = "either rest nor sru configuration given"
            raise RuntimeError(msg)

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
