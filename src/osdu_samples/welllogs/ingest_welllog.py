"""ingest-welllog — ingest a WellLog (typed schema) and its bulk data.

Reads a typed WellLog `data` document (the bundled `sample_data/welllog-data.json`
unless `DEMO_WELLLOG_DATA_FILE` points elsewhere), deserializes it into the typed
1.4.0 model, fills the envelope (ACL / legal / parent WellboreID) from config,
creates the record, then writes bulk Parquet matching the declared curves.
"""

from __future__ import annotations

import json
import math
from importlib import resources

import pyarrow as pa
from osdu_models.workproductcomponent.well_log.v1_4_0 import Data

from ..context import SampleContext
from ..registry import sample
from ._common import build_record


def _load_data(ctx: SampleContext) -> Data:
    if ctx.demo.well_log_data_file:
        with open(ctx.demo.well_log_data_file, encoding="utf-8") as fh:
            raw = json.load(fh)
    else:
        text = resources.files("osdu_samples.sample_data").joinpath("welllog-data.json").read_text()
        raw = json.loads(text)
    return Data.model_validate(raw)


def _synthetic_bulk(data: Data, rows: int = 100) -> pa.Table:
    """Generate a Table whose columns match the WellLog's curve mnemonics."""
    mnemonics = [c.Mnemonic or c.CurveID for c in (data.Curves or [])] or ["MD"]
    top = data.TopMeasuredDepth or 0.0
    bottom = data.BottomMeasuredDepth or (top + rows)
    step = (bottom - top) / (rows - 1) if rows > 1 else 0.0
    index = [top + i * step for i in range(rows)]
    cols = {}
    for i, m in enumerate(mnemonics):
        cols[m] = index if i == 0 else [math.sin(x / 50.0) * (i * 10) + 50 for x in index]
    return pa.table(cols)


@sample("ingest-welllog", "Ingest a WellLog (typed schema) and its bulk data from files.", writes=True)
def run(ctx: SampleContext) -> None:
    ctx.demo.require("wellbore_id", "legal_tag", "acl_owner", "acl_viewer")

    data = _load_data(ctx)
    data.WellboreID = ctx.demo.wellbore_id  # parent reference comes from config

    record = build_record(
        data=data.model_dump(by_alias=True, exclude_none=True),
        acl_owner=ctx.demo.acl_owner,
        acl_viewer=ctx.demo.acl_viewer,
        legal_tag=ctx.demo.legal_tag,
    )
    resp = ctx.osdu.wellbore_ddms.post_welllog_osdu(body=[record])
    record_ids = getattr(resp, "record_ids", None) or []
    if not record_ids:
        ctx.kv("create", "no record id returned")
        return
    new_id = record_ids[0]
    ctx.kv("Created WellLog", new_id)

    bulk = _synthetic_bulk(data)
    ctx.osdu.wellbore_ddms.write_bulk_parquet(new_id, bulk)
    ctx.kv("Wrote bulk rows", bulk.num_rows)
    ctx.kv("curves", bulk.column_names)
    print(f"\n  Read it back with:  osdu-samples get-welllog read-bulk-data --id {new_id}")
