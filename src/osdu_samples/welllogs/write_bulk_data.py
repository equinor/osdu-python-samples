"""write-bulk-data — write bulk curve data to a WellLog, creating a new version.

Builds a small pandas DataFrame (columns = curve mnemonics) and writes it via
the client's Parquet helper. Requires the `parquet` extra.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..context import SampleContext
from ..registry import sample


@sample("write-bulk-data", "Write bulk curve data to a WellLog (/data).", writes=True)
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()

    rows = 100
    md = np.linspace(1234.5, 2345.6, rows)
    df = pd.DataFrame({"MD": md, "GR": np.sin(md / 50.0) * 40 + 80})

    ctx.osdu.wellbore_ddms.write_bulk_parquet(record_id, df)
    ctx.kv("Wrote bulk data to", record_id)
    ctx.kv("rows", rows)
    ctx.kv("columns", list(df.columns))
