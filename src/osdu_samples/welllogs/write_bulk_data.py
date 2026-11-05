"""write-bulk-data — write bulk curve data to a WellLog, creating a new version.

Builds a small pyarrow Table (columns = curve mnemonics) and writes it via the
client's Parquet helper. Requires the `parquet` extra (which provides pyarrow).
"""

from __future__ import annotations

import math

import pyarrow as pa

from ..context import SampleContext
from ..registry import sample


@sample("write-bulk-data", "Write bulk curve data to a WellLog (/data).", writes=True)
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()

    rows = 100
    start, stop = 1234.5, 2345.6
    step = (stop - start) / (rows - 1)
    md = [start + i * step for i in range(rows)]
    gr = [math.sin(x / 50.0) * 40 + 80 for x in md]
    table = pa.table({"MD": md, "GR": gr})

    ctx.osdu.wellbore_ddms.write_bulk_parquet(record_id, table)
    ctx.kv("Wrote bulk data to", record_id)
    ctx.kv("rows", rows)
    ctx.kv("columns", table.column_names)
