"""create-welllog — create a WellLog from a typed schema model.

Authoring with `osdu_models` gives autocomplete + validation on the `data`
block; `model_dump(by_alias=True, exclude_none=True)` bridges it into the
free-form `data` the client's `Record` carries.
"""

from __future__ import annotations

from osdu_models.workproductcomponent.well_log.v1_4_0 import Curve, Data

from ..context import SampleContext
from ..registry import sample
from ._common import build_record


@sample("create-welllog", "Create a WellLog from a typed schema model.", writes=True)
def run(ctx: SampleContext) -> None:
    ctx.demo.require("wellbore_id", "legal_tag", "acl_owner", "acl_viewer")

    data = Data(
        WellboreID=ctx.demo.wellbore_id,
        Name="osdu-python-samples synthetic WellLog",
        TopMeasuredDepth=1234.5,
        BottomMeasuredDepth=2345.6,
        Curves=[
            Curve(CurveID="MD", Mnemonic="MD", NumberOfColumns=1),
            Curve(CurveID="GR", Mnemonic="GR", NumberOfColumns=1),
        ],
    )

    record = build_record(
        data=data.model_dump(by_alias=True, exclude_none=True),
        acl_owner=ctx.demo.acl_owner,
        acl_viewer=ctx.demo.acl_viewer,
        legal_tag=ctx.demo.legal_tag,
    )

    resp = ctx.osdu.wellbore_ddms.post_welllog_osdu(body=[record])
    for rid in getattr(resp, "record_ids", None) or []:
        ctx.kv("Created WellLog", rid)
