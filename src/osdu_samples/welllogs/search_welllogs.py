"""search-welllogs — search for WellLog records by kind."""

from __future__ import annotations

from osdu_python_client.generated.search.models.query_request import QueryRequest

from ..context import SampleContext
from ..registry import sample


@sample("search-welllogs", "Search for WellLog records by kind.")
def run(ctx: SampleContext) -> None:
    dto = ctx.osdu.search.query_records(
        body=QueryRequest(kind="osdu:wks:work-product-component--WellLog:*", query="*", limit=10)
    )
    results = dto.results or []
    ctx.kv("total hits", getattr(dto, "total_count", len(results)))
    for record in results:
        props = getattr(record, "additional_properties", {})
        ctx.kv("id", props.get("id", "?"))
