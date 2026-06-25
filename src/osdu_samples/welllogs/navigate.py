"""navigate — follow WellLog -> Wellbore -> Well via data references."""

from __future__ import annotations

from ..context import SampleContext, record_data_dict
from ..registry import sample


def _strip_version(osdu_id: str) -> str:
    """OSDU references may carry a trailing `:<version>`; the get-by-id endpoints
    want the bare id. Keep the leading `partition:type:unique` and drop a numeric
    version suffix if present."""
    parts = osdu_id.split(":")
    if len(parts) == 4 and parts[3].isdigit():
        return ":".join(parts[:3])
    return osdu_id.rstrip(":")


@sample("navigate", "Follow WellLog -> Wellbore -> Well via data references.")
def run(ctx: SampleContext) -> None:
    record_id = ctx.require_well_log_id()

    well_log = record_data_dict(ctx.osdu.wellbore_ddms.get_welllog_osdu(record_id=record_id))
    ctx.kv("WellLog", record_id)

    wellbore_id = well_log.get("WellboreID")
    if not wellbore_id:
        ctx.kv("WellboreID", "(none on this WellLog)")
        return
    ctx.kv("-> WellboreID", wellbore_id)

    wellbore = record_data_dict(
        ctx.osdu.wellbore_ddms.get_wellbore_osdu(record_id=_strip_version(wellbore_id))
    )
    well_id = wellbore.get("WellID")
    ctx.kv("   Wellbore.Name", wellbore.get("FacilityName") or wellbore.get("Name"))
    if not well_id:
        ctx.kv("   WellID", "(none on this Wellbore)")
        return
    ctx.kv("   -> WellID", well_id)

    well = record_data_dict(ctx.osdu.wellbore_ddms.get_well_osdu(record_id=_strip_version(well_id)))
    ctx.kv("      Well.Name", well.get("FacilityName") or well.get("Name"))
