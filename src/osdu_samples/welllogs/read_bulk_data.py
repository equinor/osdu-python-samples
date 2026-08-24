"""read-bulk-data — read a WellLog's bulk curve data as a Parquet table.

Wellbore DDMS serves bulk data as Parquet (the performant primary format); the
client's `read_bulk_parquet` helper returns a `pyarrow.Table`. Requires the
`parquet` extra (which provides pyarrow).
"""

from __future__ import annotations

from ..context import SampleContext
from ..registry import sample


@sample("read-bulk-data", "Read a WellLog's bulk curve data (/data) as a table.")
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()
    table = ctx.osdu.wellbore_ddms.read_bulk_parquet(record_id, limit=10)
    ctx.kv("id", record_id)
    ctx.kv("columns", table.column_names)
    ctx.kv("rows (capped at 10)", table.num_rows)
    _print_table(table)


def _print_table(table, max_rows: int = 10) -> None:
    cols = table.column_names
    rows = table.slice(0, max_rows).to_pylist()
    widths = {c: max(len(c), *(len(_fmt(r.get(c))) for r in rows) if rows else [len(c)]) for c in cols}
    header = "  ".join(c.rjust(widths[c]) for c in cols)
    print(header)
    for r in rows:
        print("  ".join(_fmt(r.get(c)).rjust(widths[c]) for c in cols))


def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    return "" if value is None else str(value)
