# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Command line interface to interact with the Alma-Connector module."""

from csv import DictReader
from dataclasses import dataclass
from time import sleep
from typing import cast

from click import BOOL, STRING, echo, group, option, secho
from click_option_group import optgroup
from flask import current_app
from flask.cli import with_appcontext
from flask_principal import Identity

from .click_param_type import CSV, JSON
from .decorators import build_identity, build_service
from .proxies import current_alma
from .services import AlmaRESTService, AlmaSRUService

MAX_RETRY_COUNT = 3
"""There could be problems with opensearch connections. This is the retry counter."""


@dataclass(frozen=True)
class Color:
    """The class is for the output color management."""

    neutral = "white"
    error = "red"
    warning = "yellow"
    abort = "magenta"
    success = "green"
    alternate = ("blue", "cyan")


def get_config[T](key: str, _: type[T]) -> T:
    """Get casted config from current_app."""
    return cast(T, current_app.config.get(key))


@group()
@with_appcontext
def alma() -> None:
    """Alma CLI."""


@alma.group("import")
def import_into_repo() -> None:
    """Import from Alma into repository."""


@import_into_repo.command("workflows")
def show_import_workflows() -> None:
    """Show registered update workflow types."""
    import_funcs = get_config("ALMA_REPOSITORY_RECORDS_IMPORT_FUNCS", dict)

    for key in import_funcs:
        echo(f"workflow type: {key} is registered")


@import_into_repo.command("sru")
@option(
    "--workflow",
    type=STRING,
    required=False,
    default=None,
    help="default is first of the possible dict",
)
@optgroup.group("Request Configuration", help="The Configuration for the request")
@optgroup.option("--search-key", type=STRING, required=True)
@optgroup.option("--domain", type=STRING, required=True)
@optgroup.option("--institution-code", type=STRING, required=True)
@optgroup.group("Manually set the values to search and import")
@optgroup.option(
    "--metadata",
    type=JSON(["ac_number", "filename", "access", "marcid"]),
    help="dict with ac-number, filename, access, marcid",
)
@optgroup.option("--user-email", type=STRING, default="alma@tugraz.at")
@optgroup.group("Import by file list")
@optgroup.option("--csv-file", type=CSV())
@build_service
@build_identity
def import_using_sru(
    workflow: str,
    metadata: dict,
    csv_file: DictReader,
    identity: Identity,
    alma_service: AlmaSRUService,
) -> None:
    """Search on the SRU service of alma."""
    import_funcs = get_config("ALMA_REPOSITORY_RECORDS_IMPORT_FUNCS", dict)

    if workflow is None:
        workflow = list(import_funcs.keys()).pop()

    try:
        import_func = import_funcs[workflow]
    except KeyError as error:
        secho(str(error), fg=Color.error)
        return

    list_of_items = csv_file or [metadata]

    for row in list_of_items:
        if len(row["ac_number"]) == 0:
            continue

        try:
            record = import_func(identity, **row, alma_service=alma_service)
            secho(
                f"record.id: {record.id}, ac_number: {row["ac_number"]}",
                fg=Color.success,
            )
        except RuntimeError as error:
            secho(str(error), fg=Color.error)

        # cool down the opensearch indexing process. necessary for
        # multiple imports in a short timeframe
        sleep(100)


@alma.group()
def create() -> None:
    """Create record in Alma from repository."""


@create.command("workflows")
def show_create_workflows() -> None:
    """Show registered update workflow types."""
    create_funcs = get_config("ALMA_ALMA_RECORDS_CREATE_FUNCS", dict)

    for key in create_funcs:
        echo(f"workflow type: {key} is registered")


@create.command("alma-record")
@option(
    "--metadata",
    type=JSON(),
    required=True,
    help="dictionary to parameters to create_func, depends on the used create_func methods parameters",
)
@option("--user-email", type=STRING, default="alma@tugraz.at")
@option("--api-key", type=STRING, required=True)
@option("--api-host", type=STRING, required=True)
@option(
    "--workflow",
    type=STRING,
    required=False,
    default=None,
    help="default is first of the possible dict",
)
@build_service
@build_identity
def cli_create_alma_record(
    metadata: dict,
    identity: Identity,
    alma_service: AlmaRESTService,
    workflow: str,
) -> None:
    """Create alma record."""
    create_funcs = get_config("ALMA_ALMA_RECORDS_CREATE_FUNCS", dict)

    if workflow is None:
        workflow = list(create_funcs.keys()).pop()

    try:
        create_funcs[workflow](identity, alma_service, **metadata)
    except KeyError as error:
        secho(str(error), fg=Color.error)
    except (RuntimeError, RuntimeWarning) as error:
        secho(str(error), fg=Color.error)


@alma.group()
def update() -> None:
    """Update record in repository from Alma."""


@update.command("workflows")
def show_update_workflows() -> None:
    """Show registered update workflow types."""
    update_funcs = get_config("ALMA_REPOSITORY_RECORDS_UPDATE_FUNCS", dict)

    for key in update_funcs:
        echo(f"workflow type: {key} is registered")


@update.command("repository-record")
@option(
    "--metadata",
    type=JSON(),
    help="dict with marc-id, alma identifier",
)
@option("--user-email", type=STRING, default="alma@tugraz.at")
@option("--keep-access-as-is", type=BOOL, is_flag=True, default=False)
@option(
    "--workflow",
    type=STRING,
    required=False,
    default=None,
    help="default is first of the possible dict",
)
@optgroup.group("Alma REST config (rest is prefered used over sru if both are given)")
@optgroup.option("--api-key", type=STRING)
@optgroup.option("--api-host", type=STRING)
@optgroup.group("Alma SRU config")
@optgroup.option("--search-key", type=STRING)
@optgroup.option("--domain", type=STRING)
@optgroup.option("--institution-code", type=STRING)
@build_identity
@build_service
def cli_update_repository_record(
    metadata: dict,
    identity: Identity,
    alma_service: AlmaRESTService | AlmaSRUService,
    workflow: str,
    *,
    keep_access_as_is: bool,
) -> None:
    """Update Repository record."""
    update_funcs = get_config("ALMA_REPOSITORY_RECORDS_UPDATE_FUNCS", dict)

    if workflow is None:
        workflow = list(update_funcs.keys()).pop()

    try:
        update_funcs[workflow](
            identity=identity,
            alma_service=alma_service,
            update_access=not keep_access_as_is,
            **metadata,
        )
    except KeyError as error:
        secho(str(error), fg=Color.error)
    except (RuntimeError, RuntimeWarning) as error:
        secho(str(error), fg=Color.error)


@update.command("url-in-alma")
@option(
    "--csv-file",
    type=CSV(header="mms_id,new_url"),
    required=True,
    help="two columns: mms_id and new_url",
)
def update_url_in_alma(csv_file: DictReader) -> None:
    """Update url in remote repository records.

    :params csv_file (file) with two columns mms_id and new_url
    """
    for mms_id, new_url in csv_file:
        current_alma.alma_rest_service.update_field(mms_id, "856.4._.u", new_url)


@update.command("field")
@option("--mms-id", type=STRING, required=True)
@option(
    "--field-json-path",
    type=STRING,
    required=True,
    help="e.g. 100.1._.u",
)
@option("--new-subfield-value", type=STRING, required=True)
def update_field(mms_id: str, field_json_path: str, new_subfield_value: str) -> None:
    """Update field."""
    service = current_alma.alma_rest_service
    service.update_field(mms_id, field_json_path, new_subfield_value)
