# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the Alma-Connector module."""

import click


@click.group()
def alma():
    """Alma CLI."""


@alma.command()
@click.option("--mms-id", type=click.STRING, require=True)
def show(mms_id):
    pass
