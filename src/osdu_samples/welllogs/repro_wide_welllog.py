"""repro-wide-welllog — reproduce the wide-WellLog ingestion timeout.

Background: users report that ingesting a WellLog *metadata* record with more
than ~400 curves times out. Neither Wellbore DDMS nor the Storage service
imposes a curve-count cap, and both process the record in linear time — so a
sharp threshold points at an environmental limit (an API gateway / ingress
body-size or upstream-timeout policy, or the DDMS->storage client timeout).

This sample sweeps a range of curve counts, creating a metadata-only WellLog at
each, and times the `post_welllog_osdu` (create) call. It uses `.detailed()` so a
non-2xx response is reported (with status code) instead of raising, and classifies
each outcome so you can tell the failure modes apart:

    OK                          create succeeded
    GATEWAY body-size (413)     payload exceeded an ingress/gateway limit
    GATEWAY/upstream timeout     502 / 504 from a proxy in front of the service
    DDMS->storage timeout (~10s) 5xx returned around the DDMS client timeout
    CLIENT timeout/transport     the call hung / connection dropped

Created records are deleted again (best-effort) so the sweep leaves nothing
behind. Curve counts come from `--curves` (default: 100,200,400,600,800).

    osdu-samples repro-wide-welllog --write --curves 300,400,500
"""

from __future__ import annotations

import time

from osdu_models.workproductcomponent.well_log.v1_4_0 import Curve, Data

from ..context import SampleContext
from ..registry import sample
from ._common import build_record

DEFAULT_SWEEP = (100, 200, 400, 600, 800)


def _build_wide_record(ctx: SampleContext, n_curves: int):
    data = Data(
        WellboreID=ctx.demo.wellbore_id,
        Name=f"repro-wide-welllog {n_curves} curves",
        TopMeasuredDepth=1234.5,
        BottomMeasuredDepth=2345.6,
        ReferenceCurveID="CURVE_0",
        Curves=[
            Curve(CurveID=f"CURVE_{i}", Mnemonic=f"C{i}", NumberOfColumns=1)
            for i in range(n_curves)
        ],
    )
    return build_record(
        data=data.model_dump(by_alias=True, exclude_none=True),
        acl_owner=ctx.demo.acl_owner,
        acl_viewer=ctx.demo.acl_viewer,
        legal_tag=ctx.demo.legal_tag,
    )


def _status_code(resp) -> int | None:
    status = getattr(resp, "status_code", None)
    if status is None:
        return None
    return status.value if hasattr(status, "value") else int(status)


def _classify(status: int | None, elapsed: float) -> str:
    if status is None:
        return "CLIENT timeout/transport (call hung or connection dropped)"
    if 200 <= status < 300:
        return "OK"
    if status == 413:
        return "GATEWAY body-size limit (413 Payload Too Large)"
    if status in (502, 504):
        return f"GATEWAY/upstream timeout ({status})"
    if status >= 500 and 8.0 < elapsed < 20.0:
        return "likely DDMS->storage client timeout (~10s)"
    return f"HTTP {status}"


@sample("repro-wide-welllog", "Reproduce the wide-WellLog (>N curves) ingestion timeout.", writes=True)
def run(ctx: SampleContext) -> None:
    ctx.demo.require("wellbore_id", "legal_tag", "acl_owner", "acl_viewer")
    counts = ctx.curve_counts or DEFAULT_SWEEP

    print(f"{'curves':>7} {'status':>7} {'elapsed_s':>10}  classification")
    print("  " + "-" * 70)

    created: list[str] = []
    op = ctx.osdu.wellbore_ddms.post_welllog_osdu
    for n in counts:
        record = _build_wide_record(ctx, n)
        t0 = time.perf_counter()
        try:
            resp = op.detailed(body=[record])
            elapsed = time.perf_counter() - t0
            status = _status_code(resp)
            parsed = getattr(resp, "parsed", None)
            created.extend(getattr(parsed, "record_ids", None) or [])
        except Exception as e:  # noqa: BLE001 — timeouts/transport errors are the thing we hunt
            elapsed = time.perf_counter() - t0
            status = None
            print(f"{n:>7} {'-':>7} {elapsed:>10.2f}  {_classify(status, elapsed)}: {type(e).__name__}")
            continue
        print(f"{n:>7} {str(status):>7} {elapsed:>10.2f}  {_classify(status, elapsed)}")

    _cleanup(ctx, created)


def _cleanup(ctx: SampleContext, record_ids: list[str]) -> None:
    if not record_ids:
        return
    deleted = 0
    for rid in record_ids:
        try:
            ctx.osdu.wellbore_ddms.del_osdu_welllog(record_id=rid)
            deleted += 1
        except Exception:  # noqa: BLE001 — cleanup is best-effort
            pass
    ctx.kv("cleaned up records", f"{deleted}/{len(record_ids)}")
