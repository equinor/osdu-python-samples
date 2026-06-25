"""read-bulk-data — read a WellLog's bulk curve data as a Parquet table.

Wellbore DDMS serves bulk data as Parquet (the performant primary format); the
client's `read_bulk_parquet` helper returns a `pyarrow.Table` (or a pandas
DataFrame with `as_dataframe=True`). Requires the `parquet` extra.
"""

from __future__ import annotations

from ..context import SampleContext
from ..registry import sample


@sample("read-bulk-data", "Read a WellLog's bulk curve data (/data) as a table.")
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()
    df = ctx.osdu.wellbore_ddms.read_bulk_parquet(record_id, limit=10, as_dataframe=True)
    ctx.kv("id", record_id)
    ctx.kv("columns", list(df.columns))
    ctx.kv("rows (capped at 10)", len(df))
    print(df.to_string(max_rows=10))
