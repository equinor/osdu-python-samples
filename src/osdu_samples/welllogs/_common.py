"""Shared constants and record-building helpers for the WellLog samples."""

from __future__ import annotations

from typing import Any

from osdu_python_client.generated.wellbore_ddms.models.legal import Legal
from osdu_python_client.generated.wellbore_ddms.models.record import Record
from osdu_python_client.generated.wellbore_ddms.models.record_data import RecordData
from osdu_python_client.generated.wellbore_ddms.models.storage_acl import StorageAcl

# These samples target WellLog schema 1.4.0.
WELLLOG_KIND = "osdu:wks:work-product-component--WellLog:1.4.0"


def build_record(data: dict[str, Any], acl_owner: str, acl_viewer: str, legal_tag: str,
                 record_id: str | None = None) -> Record:
    """Wrap a typed-then-dumped `data` dict in the OSDU record envelope the
    client expects (kind + acl + legal + data)."""
    record = Record(
        kind=WELLLOG_KIND,
        acl=StorageAcl(owners=[acl_owner], viewers=[acl_viewer]),
        legal=Legal(legaltags=[legal_tag], other_relevant_data_countries=["US"]),
        data=RecordData.from_dict(data),
    )
    if record_id:
        record.id = record_id
    return record
