# ruff: noqa: I001, F401
"""Importing this package registers every WellLog sample.

Import order == registration order == the order `run-all` and `list` use, so it
is pinned here (isort disabled for this file) to mirror the C# samples table.
"""

from __future__ import annotations

from . import (
    service_info,
    search_welllogs,
    get_welllog,
    welllog_versions,
    navigate,
    read_bulk_data,
    bulk_statistics,
    create_welllog,
    write_bulk_data,
    ingest_welllog,
    delete_welllog,
    repro_wide_welllog,
)
