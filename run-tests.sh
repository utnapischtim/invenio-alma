#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

# Usage:
#   env DB=postgresql12 SEARCH=elasticsearch7 CACHE=redis MQ=rabbitmq ./run-tests.sh

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

ruff check .

python -m pytest -s
