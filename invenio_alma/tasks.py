# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Celery Tasks for invenio-alma."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity

from .proxies import current_alma


@shared_task(ignore_result=True)
def create_alma_records(workflow: str | None = None) -> None:
    """Create records within alma from repository records."""
    current_app.logger.info("start creating records in alma")

    aggregators = current_app.config["ALMA_ALMA_RECORDS_CREATE_AGGREGATORS"]
    create_funcs = current_app.config["ALMA_ALMA_RECORDS_CREATE_FUNCS"]

    if workflow is None:
        if list(create_funcs.keys()).pop() != list(aggregators.keys()).pop():
            msg = "ERROR: create_funcs and aggregators are not configured with same workflow."
            current_app.logger.error(msg)
            return
        workflow = list(create_funcs.keys()).pop()

    if not aggregators:
        msg = "ERROR: variable ALMA_REPOSITORY_RECORDS_CREATE_AGGREGATORS not set."
        current_app.logger.error(msg)
        return

    if not create_funcs:
        msg = "ERROR: variable ALMA_ALMA_RECORDS_CREATE_FUNCS not set"
        current_app.logger.error(msg)
        return

    alma_service = current_alma.alma_rest_service

    try:
        aggregator = aggregators[workflow]
        create_func = create_funcs[workflow]
    except KeyError:
        msg = "ERROR: creating record in alma with type %s didn't work."
        current_app.logger.error(msg, workflow)
        return

    for entry in aggregator():
        try:
            create_func(system_identity, entry.pid, entry.cms_id, alma_service)
            msg = "record %s has been updated successfully."
            current_app.logger.info(msg, entry.pid)
        except (RuntimeError, RuntimeWarning) as error:
            msg = "ERROR: creating record in alma. (marcid: %s, cms_id: %s, error: %s)"
            current_app.logger.error(msg, entry.pid, entry.cms_id, error)


@shared_task(ignore_result=True)
def update_repository_records(workflow: str | None = None) -> None:
    """Update records within the repository from alma records."""
    current_app.logger.info("start updating records in repository from alma")

    aggregators = current_app.config["ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS"]
    update_funcs = current_app.config["ALMA_REPOSITORY_RECORDS_UPDATE_FUNCS"]

    if workflow is None:
        if list(update_funcs.keys()).pop() != list(aggregators.keys()).pop():
            msg = "ERROR: update_funcs and aggregators are not configured with same workflow."
            current_app.logger.error(msg)
            return
        workflow = list(update_funcs.keys()).pop()

    if not aggregators:
        msg = "ERROR: variable ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS not set."
        current_app.logger.error(msg)
        return

    if not update_funcs:
        msg = "ERROR: variable ALMA_REPOSITORY_RECORDS_UPDATE_FUNCS not set."
        current_app.logger.error(msg)
        return

    alma_service = current_alma.alma_sru_service

    try:
        aggregator = aggregators[workflow]
        update_func = update_funcs[workflow]
    except KeyError:
        msg = "ERROR: updating record in alma with type %s didn't work."
        current_app.logger.error(msg, workflow)
        return

    for entry in aggregator():
        try:
            update_func(system_identity, entry.pid, entry.cms_id, alma_service)
            msg = "record %s has been updated successfully."
            current_app.logger.info(msg, entry.pid)
        except (RuntimeError, RuntimeWarning) as error:
            msg = "ERROR: updating records within the repository."
            msg += " (marc21_id: %s, cms_id: %s, error: %s)"
            current_app.logger.error(msg, entry.pid, entry.cms_id, error)
