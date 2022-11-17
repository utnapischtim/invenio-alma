# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery Tasks for invenio-alma."""

from celery import shared_task
from flask import current_app
from flask_mail import Message

from .api import create_alma_record, update_repository_record
from .utils import apply_aggregators, preliminaries


def config_variables():
    """Configuration variables."""
    user_email = current_app.config["ALMA_USER_EMAIL"]
    api_key = current_app.config["ALMA_API_KEY"]
    sender = current_app.config["ALMA_ERROR_MAIL_SENDER"]
    recipients = ",".join(current_app.config["ALMA_ERROR_MAIL_RECIPIENTS"])

    return user_email, api_key, sender, recipients


@shared_task(ignore_result=True)
def create_alma_records():
    """Create records within alma from repository records."""
    user_email, api_key, sender, recipients = config_variables()
    aggregators = current_app.config["ALMA_ALMA_RECORDS_CREATE_AGGREGATORS"]

    marc_ids = apply_aggregators(aggregators)
    records_service, alma_service, identity = preliminaries(user_email)

    alma_service.config.api_key = api_key

    for marc_id in marc_ids:
        try:
            create_alma_record(records_service, alma_service, identity, marc_id)
        # pylint: disable=broad-except
        except Exception:
            msg = Message(
                "ERROR: creating record in alma.",
                sender=sender,
                recipients=recipients,
                body=f"marc_id: {marc_id}",
            )
            current_app.extensions["mail"].send(msg)


@shared_task(ignore_result=True)
def update_repository_records():
    """Update records within the repository from alma records."""
    user_email, api_key, sender, recipients = config_variables()
    aggregators = current_app.config["ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS"]

    records = apply_aggregators(aggregators)
    records_service, alma_service, identity = preliminaries(user_email, use_sru=True)

    alma_service.config.api_key = api_key

    for marc_id, alma_id in records:
        try:
            update_repository_record(
                records_service, alma_service, marc_id, identity, alma_id
            )
        # pylint: disable=broad-except
        except Exception:
            msg = Message(
                "ERROR: updating records within the repository.",
                sender=sender,
                recipients=recipients,
                body=f"marc21_id: {marc_id}, alma_id: {alma_id}",
            )
            current_app.extensions["mail"].send(msg)
