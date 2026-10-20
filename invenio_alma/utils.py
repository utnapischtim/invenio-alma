# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Utils."""

from __future__ import annotations

import functools
from collections.abc import Callable
from datetime import datetime

from .proxies import current_alma
from .services.errors import AlmaAPIError


def is_duplicate_in_alma(cms_id: str) -> bool:
    """Check if there is already a record in alma."""
    sru_service = current_alma.alma_sru_service
    search_key = "local_field_995"

    try:
        record = sru_service.get_record(cms_id, search_key)
        return len(record) > 0
    except AlmaAPIError:
        return False


def apply_aggregators[T](aggregators: list[Callable[[], list[T]]]) -> list:
    """Apply aggregators."""

    def func(accumulator: list[T], aggregator: Callable[[], list[T]]) -> list[T]:
        return accumulator + aggregator()

    return functools.reduce(func, aggregators, [])


def validate_date(date: str) -> bool:
    """Validate date to be YYYY-MM-DD."""
    try:
        temp = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")  # noqa: DTZ007
        return date == temp
    except ValueError:
        return False
