"""Deterministic, byte-exact, preservation-only import primitives.

Implements the bounded in-memory INF-01–INF-04 prototype. Durable storage,
transactional persistence and cancellation remain unimplemented (INF-05).
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal


class ArchiveError(ValueError):
    """An archive contract or resource-limit violation."""


@dataclass(frozen=True)
class Limits:
    maxBytes: int
    maxPhysicalSpans: int
    maxLogicalRecords: int
    maxContinuationBytes: int
    maxExpandedSelection: int
    maxCpuMillis: int
    maxWallMillis: int
    maxResidentBytes: int

    def __post_init__(self) -> None:
        for name, value in vars(self).items():
            if type(value) is not int or value <= 0:
                raise ArchiveError(f"{name} must be a positive integer")


@dataclass(frozen=True)
class Archive:
    sourceHash: str
    byteLength: int
    originalFilename: str
    declaredExtension: str
    projectRef: str
    namespace: str
    policyId: str
    sourceBytes: bytes

    def retrieve(self) -> bytes:
        if len(self.sourceBytes) != self.byteLength or sha256(self.sourceBytes).hexdigest() != self.sourceHash:
            raise ArchiveError("HASH_MISMATCH")
        return self.sourceBytes


def archive_bytes(data: bytes, *, filename: str, extension: str,
                  project_ref: str, namespace: str, policy_id: str,
                  limits: Limits) -> Archive:
    if not isinstance(data, bytes):
        raise ArchiveError("source must be bytes")
    if len(data) > limits.maxBytes:
        raise ArchiveError("MAX_BYTES_EXCEEDED")
    if not all(isinstance(v, str) and v for v in (filename, project_ref, namespace, policy_id)):
        raise ArchiveError("filename, project_ref, namespace and policy_id are required")
    return Archive(sha256(data).hexdigest(), len(data), filename, extension,
                   project_ref, namespace, policy_id, bytes(data))


@dataclass(frozen=True)
class PhysicalSpan:
    ordinal: int
    startByte: int
    endByte: int
    kind: str = "opaque"
    decodedLine: int | None = None


@dataclass(frozen=True)
class SpanLedger:
    sourceHash: str
    revision: int
    spans: tuple[PhysicalSpan, ...]


def validate_spans(archive: Archive, spans: tuple[PhysicalSpan, ...], *, limits: Limits) -> SpanLedger:
    if len(spans) > limits.maxPhysicalSpans:
        raise ArchiveError("MAX_PHYSICAL_SPANS_EXCEEDED")
    cursor = 0
    for ordinal, span in enumerate(spans):
        if span.ordinal != ordinal or span.startByte != cursor or span.endByte <= cursor:
            raise ArchiveError("INVALID_SPAN_COVERAGE")
        if span.decodedLine is not None and span.decodedLine < 1:
            raise ArchiveError("INVALID_DECODED_LINE")
        cursor = span.endByte
    if cursor != archive.byteLength:
        raise ArchiveError("INVALID_SPAN_COVERAGE")
    return SpanLedger(archive.sourceHash, 0, spans)


def entity_id(namespace: str, profile_family: str, entity_kind: str,
              source_identifier: str, scope_identifier: str) -> str:
    values = [namespace, profile_family, entity_kind, source_identifier, scope_identifier]
    if any(not isinstance(v, str) for v in values):
        raise ArchiveError("identity fields must be strings")
    if not entity_kind.isascii() or not entity_kind or not all(c.isalnum() or c == '_' for c in entity_kind):
        raise ArchiveError("invalid entity kind")
    raw = json.dumps(values, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return entity_kind + ':' + sha256(raw).hexdigest()


STAGES = ('preserved', 'parsed', 'understood', 'mapped', 'visualized',
          'exported', 'analysis', 'equivalence')


def fidelity_report(archive: Archive) -> dict[str, object]:
    """Preservation-only stage report; no parser or Core mapping claims."""
    return {'sourceHash': archive.sourceHash,
            'byteLength': archive.byteLength,
            'stages': {stage: ('succeeded' if stage == 'preserved' else 'not-attempted')
                       for stage in STAGES}, 'coreModel': None}
