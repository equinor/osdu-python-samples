"""service-info — print Wellbore DDMS service info (`/about`)."""

from __future__ import annotations

from ..context import SampleContext
from ..registry import sample


@sample("service-info", "Print Wellbore DDMS service info (/about).")
def run(ctx: SampleContext) -> None:
    about = ctx.osdu.wellbore_ddms.get_about()
    ctx.kv("service", getattr(about, "service", "wellbore-ddms"))
    ctx.kv("version", getattr(about, "version", "?"))
    ctx.kv("build", getattr(about, "build_number", getattr(about, "buildNumber", "?")))
