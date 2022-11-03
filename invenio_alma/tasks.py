# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery Tasks for invenio-alma."""

import traceback

from celery import shared_task
from flask import current_app
from flask_mail import Message

from .utils import (
    calculate_to_create_alma_records,
    calculate_to_update_repository_records,
    create_alma_record,
    preliminaries,
    update_repository_record,
)


@shared_task(ignore_result=True)
def create_alma_records():
    """Create records within alma from repository records."""
    user_email = current_app.config["INVENIO_ALMA_USER_EMAIL"]
    api_key = current_app.config["INVENIO_ALMA_API_KEY"]
    aggregators = current_app.config["INVENIO_ALMA_ALMA_RECORDS_CREATE_AGGREGATORS"]

    marc_ids = calculate_to_create_alma_records(aggregators)
    records_service, alma_service, identity = preliminaries(user_email)

    alma_service.config.api_key = api_key

    for marc_id in marc_ids:
        try:
            create_alma_record(records_service, alma_service, identity, marc_id)
        except Exception:
            msg = Message(
                "Something went wrong when creating the alma record.",
                sender=current_app.config["INVENIO_ALMA_ERROR_MAIL_SENDER"],
                recipients=current_app.config["INVENIO_ALMA_ERROR_MAIL_RECIPIENTS"],
                body=traceback.format_exc(),
            )
            current_app.extensions["mail"].send(msg)


@shared_task(ignore_result=True)
def update_repository_records():
    """Update records within the repository from alma records."""
    user_email = current_app.config["INVENIO_ALMA_USER_EMAIL"]
    api_key = current_app.config["INVENIO_ALMA_API_KEY"]
    aggregators = current_app.config[
        "INVENIO_ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS"
    ]

    records = calculate_to_update_repository_records(aggregators)
    records_service, alma_service, identity = preliminaries(user_email, use_sru=True)

    alma_service.config.api_key = api_key

    for marc_id, alma_id in records:
        try:
            update_repository_record(
                records_service, alma_service, marc_id, identity, alma_id
            )
        except Exception:
            msg = Message(
                "Something went wrong when updating records.",
                sender=current_app.config["INVENIO_ALMA_ERROR_MAIL_SENDER"],
                recipients=current_app.config["INVENIO_ALMA_ERROR_MAIL_RECIPIENTS"],
                body=traceback.format_exc(),
            )
            current_app.extensions["mail"].send(msg)
