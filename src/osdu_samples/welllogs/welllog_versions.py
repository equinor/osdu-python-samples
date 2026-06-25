"""welllog-versions — list all stored versions of a WellLog."""

from __future__ import annotations

from ..context import SampleContext
from ..registry import sample


@sample("welllog-versions", "List all stored versions of a WellLog.")
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()
    dto = ctx.osdu.wellbore_ddms.get_osdu_welllog_versions(record_id=record_id)
    versions = getattr(dto, "versions", None) or []
    ctx.kv("id", record_id)
    ctx.kv("version count", len(versions))
    for v in versions:
        ctx.kv("  version", v)
