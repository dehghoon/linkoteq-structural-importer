"""Preservation-only infrastructure for Linkoteq structural imports."""
from .preservation import (Limits, Archive, ArchiveError, PhysicalSpan, SpanLedger,
                           archive_bytes, entity_id, validate_spans, fidelity_report)

__all__ = ["Limits", "Archive", "ArchiveError", "PhysicalSpan", "SpanLedger",
           "archive_bytes", "entity_id", "validate_spans", "fidelity_report"]
