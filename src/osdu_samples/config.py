"""Demo configuration, read from `DEMO_*` environment variables (or a `.env`).

The OSDU connection/auth config (`SERVER`, `DATA_PARTITION_ID`, `AUTH_*`, ...) is
owned and read by `osdu-python-client`; this module only carries the extra knobs
the samples themselves need (which WellLog to read, ACL/legal for writes, ...).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass
class DemoOptions:
    """Sample inputs, mirroring the `Demo` section of the C# samples."""

    well_log_id: str = ""
    wellbore_id: str = ""
    legal_tag: str = ""
    acl_owner: str = ""
    acl_viewer: str = ""
    well_log_data_file: str = ""
    allow_writes: bool = False

    @classmethod
    def from_env(cls) -> DemoOptions:
        return cls(
            well_log_id=_env("DEMO_WELLLOG_ID"),
            wellbore_id=_env("DEMO_WELLBORE_ID"),
            legal_tag=_env("DEMO_LEGAL_TAG"),
            acl_owner=_env("DEMO_ACL_OWNER"),
            acl_viewer=_env("DEMO_ACL_VIEWER"),
            well_log_data_file=_env("DEMO_WELLLOG_DATA_FILE"),
            allow_writes=_env("DEMO_ALLOW_WRITES").lower() in {"1", "true", "yes"},
        )

    def require(self, *fields: str) -> None:
        """Raise a friendly error if any required DEMO_* field is empty."""
        missing = [f for f in fields if not getattr(self, f)]
        if missing:
            names = ", ".join(f"DEMO_{f.upper()}" for f in missing)
            raise SampleConfigError(f"This sample requires: {names}")


class SampleConfigError(RuntimeError):
    """Raised when required demo configuration is missing."""
