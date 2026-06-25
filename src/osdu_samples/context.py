"""`SampleContext` — the handle every sample receives.

Bundles the live `OsduClient`, the resolved `DemoOptions`, and a couple of small
print/data helpers so the individual sample files stay focused on the SDK call
they are demonstrating.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from osdu_python_client import OsduClient

from .config import DemoOptions


@dataclass
class SampleContext:
    osdu: OsduClient
    demo: DemoOptions
    id_override: str = ""
    curve_counts: tuple[int, ...] = ()  # for the repro sample; set by --curves

    @property
    def well_log_id(self) -> str:
        """The WellLog id to operate on: `--id` wins over `DEMO_WELLLOG_ID`."""
        return self.id_override or self.demo.well_log_id

    def require_well_log_id(self) -> str:
        if not self.well_log_id:
            from .config import SampleConfigError

            raise SampleConfigError("This sample requires: DEMO_WELLLOG_ID (or --id)")
        return self.well_log_id

    # --- presentation helpers -------------------------------------------------
    @staticmethod
    def heading(text: str) -> None:
        print(f"\n=== {text} ===")

    @staticmethod
    def kv(key: str, value: Any) -> None:
        print(f"  {key}: {value}")


def record_data_dict(record: Any) -> dict[str, Any]:
    """Pull the free-form `data` block out of a parsed record, regardless of
    whether the client surfaced it as a generated model or a plain dict."""
    data = getattr(record, "data", record)
    if hasattr(data, "additional_properties"):
        return dict(data.additional_properties)
    if hasattr(data, "to_dict"):
        return data.to_dict()
    return dict(data or {})
