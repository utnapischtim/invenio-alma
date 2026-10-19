# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alma Service config class."""

from dataclasses import dataclass


@dataclass
class AlmaRESTConfig:
    """Alma service configuration class."""

    api_key: str = ""
    api_host: str = ""
    time_out: str = ""

    @property
    def timeout(self) -> int:
        """Get timeout."""
        return int(self.time_out)


@dataclass
class AlmaSRUConfig:
    """Alma sru service config."""

    search_key: str = ""
    domain: str = ""
    institution_code: str = ""
