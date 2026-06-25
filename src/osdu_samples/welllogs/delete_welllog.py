"""delete-welllog — delete a WellLog by id."""

from __future__ import annotations

from ..context import SampleContext
from ..registry import sample


@sample("delete-welllog", "Delete a WellLog by id.", writes=True)
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()
    ctx.osdu.wellbore_ddms.del_osdu_welllog(record_id=record_id)
    ctx.kv("Deleted WellLog", record_id)
