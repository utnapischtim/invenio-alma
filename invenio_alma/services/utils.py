# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Common utils functions."""

from functools import reduce


# TODO: Move to Marc21 record module
def deep_get(obj, keys, default=None):
    """Get value from multiple keys.

    :param obj to search
    :param keys str multiple keys
    """
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        obj,
    )
