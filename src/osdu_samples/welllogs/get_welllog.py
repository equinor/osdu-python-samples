"""get-welllog — get a WellLog by id and read its `data` with typed models."""

from __future__ import annotations

from osdu_models.workproductcomponent.well_log.v1_4_0 import Data

from ..context import SampleContext, record_data_dict
from ..registry import sample


@sample("get-welllog", "Get a WellLog by id and read its data with typed schema models.")
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()
    record = ctx.osdu.wellbore_ddms.get_welllog_osdu(record_id=record_id)

    # Bridge the free-form `data` dict into the typed 1.4.0 model for safe, typed reads.
    data = Data.model_validate(record_data_dict(record))
    ctx.kv("id", record_id)
    ctx.kv("Name", data.Name)
    ctx.kv("WellboreID", data.WellboreID)
    ctx.kv("curve count", len(data.Curves or []))
    for curve in (data.Curves or [])[:10]:
        ctx.kv("  curve", curve.Mnemonic or curve.CurveID)
