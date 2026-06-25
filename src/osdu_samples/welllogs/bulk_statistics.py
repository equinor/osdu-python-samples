"""bulk-statistics — get per-curve bulk-data statistics (`/data/statistics`)."""

from __future__ import annotations

from ..context import SampleContext
from ..registry import sample


@sample("bulk-statistics", "Get per-curve bulk-data statistics (/data/statistics).")
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()
    stats = ctx.osdu.wellbore_ddms.get_ddms_v3_welllogs_record_id_data_statistics(record_id=record_id)
    ctx.kv("id", record_id)
    ctx.kv("status", getattr(stats, "computation_status", "?"))

    # Per-curve statistics live in `.data` (curve name -> values), exposed via additional_properties.
    per_curve = getattr(stats, "data", None)
    curves = getattr(per_curve, "additional_properties", None) or {}
    for name, cstat in curves.items():
        ctx.kv(f"  {name}", getattr(cstat, "additional_properties", cstat))
