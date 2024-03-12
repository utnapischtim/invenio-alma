..
    Copyright (C) 2021 Graz University of Technology.

    invenio-alma is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version v0.11.1 (release 2024-03-12)

- fix: tasks aggregator should be singular


Version v0.11.0 (release 2024-02-27)

- do: ruff suggested change
- fix: missing function get_user_by_email
- cli: add option --keep-access-as-is
- setup: readd invenio-records-marc21
- global: remove invenio-records-marc21 dep
- refactor
- tasks: add custom import_func feature


Version v0.10.2 (release 2023-09-25)

- cli: add embargo to import


Version v0.10.1 (release 2023-09-14)

- fix: refactor code to use secho instead to logger


Version v0.10.0 (release 2023-09-12)

- cli: rename command
- cli: update import_record
- ruff: update
- fix: missed update of refactoring
- cli: rename sru command
- ruff: update


Version v0.9.1 (release 2023-05-26)

- fix: changed api not applied


Version v0.9.0 (release 2023-05-26)

- ruff: add to ignore
- cli: make update func customizable


Version v0.8.2 (release 2023-05-01)

- ext: revert last change


Version v0.8.1 (release 2023-05-01)

- setup: add forgotten ruff configuration
- ext: mock the resource and service properties
- setup: re-add isort configuration


Version v0.8.0 (release 2023-04-29)

- ext: add existence check before resource creation
- global: use ruff instead of pylint
- global: add services to export
- tasks: add option to use update func
- sru: add search_key on the search


Version v0.7.6 (release 2023-04-26)

- fix: remove variable check


Version v0.7.5 (release 2023-04-26)

- create: add read permission
- feature: add item api


Version v0.7.4 (release 2023-01-26)

- fix: handle read timeout


Version v0.7.3 (release 2023-01-26)

- fix: xml does not have xpath
- cli: add cms_id to create alma-record


Version v0.7.2 (release 2023-01-19)

- fix: initialization check not possible


Version v0.7.1 (release 2023-01-13)

- setup: remove for now translations


Version v0.7.0 (release 2023-01-13)

- setup: remove python3.8 add python3.11 support
- utils: catch possible Exception
- fixes:
- global: add type hints and documentation
- theses: remove not used configuration
- theses: add duplicate check
- fix: creating records has to use rest
- setup: add celery task and translations
- fix: various errors brought up by running tests
- global: refactore plus add config variables
- global: refactore and change functionality
- cli: add command update repository record
- improve: update metadata by return of alma
- cli: implement alma create record
- service: refactore
- api: move functions to other packages


Version v0.6.0 (release 2022-10-17)

- global: migrate to reusable workflows
- setup: migrate to opensearch2


Version v0.5.0 (release 2022-10-02)

- change: add timeout to requests.(get|put)
- fix: invenio_search.engine hides used search tool
- global: add supported python versions
- global: move to reusable workflows
- global: migrate from elasticsearch to opensearch
- fix AlmaAPIError missing paramete use
- harmonize the alma service error messages
- use for duplicate error message same structure as for the others


Version v0.4.4 (release 2022-08-03)

- improve duplicate output by adding the repository id
- fix RequestError problem, by handling the error


Version v0.4.3 (release 2022-08-02)

- add ac number to the success output
- fix ValidationError problem


Version v0.4.2 (release 2022-08-02)

- remove no_self_use, pylint Closes #5502
- fix elasticsearch ConnectionTimeout import
- fix sphinx language


Version v0.4.1 (release 2022-08-02)

- fix elasticsearch ConnectionTimeout problem


Version 0.1.0 (released TBD)

- Initial public release.
