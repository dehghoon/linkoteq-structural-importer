"""Loss-preserving STAAD text lexical slice; no engineering interpretation.

Supports ASCII-compatible source lines, semicolon-separated statements and
bounded continuation. Source bytes are never modified or executed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .preservation import Archive, ArchiveError, Limits, PhysicalSpan, validate_spans


@dataclass(frozen=True)
class LexicalRecord:
    ordinal: int
    startByte: int
    endByte: int
    sourceLine: int
    text: str
    classification: Literal["statement", "comment", "blank", "opaque"]
    physicalSpanOrdinals: tuple[int, ...]


@dataclass(frozen=True)
class LexicalResult:
    profile: str
    records: tuple[LexicalRecord, ...]
    spans: tuple[PhysicalSpan, ...]
    diagnostics: tuple[str, ...]


def detect_staad(data: bytes, filename: str = "") -> str | None:
    """Conservative STAAD signature detection; extension alone is insufficient."""
    if not isinstance(data, bytes):
        raise ArchiveError("source must be bytes")
    prefix = data[:8192]
    if b"\x00" in prefix:
        return None
    # Match complete STAAD header line (allow UTF-8 BOM and leading comments).
    for line in prefix.splitlines()[:40]:
        stripped = line.strip().removeprefix(b"\xef\xbb\xbf").strip().upper()
        if stripped.startswith(b"STAAD ") and stripped[6:].split(b" ", 1)[0] in (b"SPACE", b"PLANE", b"TRUSS", b"FLOOR"):
            return "staad-text-candidate"
    return None


def _physical_lines(data: bytes) -> list[tuple[int, int, bytes]]:
    result = []
    pos = 0
    for chunk in data.splitlines(keepends=True):
        end = pos + len(chunk)
        result.append((pos, end, chunk))
        pos = end
    return result


def lex_staad(archive: Archive, *, limits: Limits) -> LexicalResult:
    """Emit byte-traceable records; do not promote any record to Core entities."""
    data = archive.retrieve()
    if len(data) > limits.maxBytes:
        raise ArchiveError("MAX_BYTES_EXCEEDED")
    profile = detect_staad(data, archive.originalFilename)
    if profile is None:
        raise ArchiveError("STAAD_SIGNATURE_NOT_FOUND")
    lines = _physical_lines(data)
    spans = tuple(PhysicalSpan(i, start, end, "source-line", i + 1)
                  for i, (start, end, _) in enumerate(lines))
    validate_spans(archive, spans, limits=limits)
    records: list[LexicalRecord] = []
    diagnostics: list[str] = []
    pending: list[tuple[int, int, bytes, int]] = []

    def emit(parts: list[tuple[int, int, bytes, int]]) -> None:
        if not parts:
            return
        start, _, _, line_id = parts[0]
        _, end, _, _ = parts[-1]
        raw = b"".join(piece for _, _, piece, _ in parts)
        if len(raw) > limits.maxContinuationBytes:
            raise ArchiveError("MAX_CONTINUATION_BYTES_EXCEEDED")
        # ASCII-compatible decoding is deliberately strict; unsupported encoding
        # stays in the original archive and is diagnosed, never silently fixed.
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
            diagnostics.append("ENCODING_UNVERIFIED_LATIN1_VIEW")
        stripped = text.strip()
        if not stripped:
            kind = "blank"
        elif stripped.startswith("*"):
            kind = "comment"
        else:
            kind = "statement"
        # Semicolons are retained within the record. Splitting without verified
        # grammar could destroy command boundaries and provenance.
        records.append(LexicalRecord(len(records), start, end, line_id + 1,
                                     text, kind, tuple(i for _, _, _, i in parts)))
        if len(records) > limits.maxLogicalRecords:
            raise ArchiveError("MAX_LOGICAL_RECORDS_EXCEEDED")

    for i, (start, end, chunk) in enumerate(lines):
        body = chunk.rstrip(b"\r\n")
        # STAAD trailing hyphen continuation is recorded, not interpreted.
        continuation = body.rstrip().endswith(b"-")
        pending.append((start, end, chunk, i))
        if sum(len(part[2]) for part in pending) > limits.maxContinuationBytes:
            raise ArchiveError("MAX_CONTINUATION_BYTES_EXCEEDED")
        if not continuation:
            emit(pending)
            pending = []
    if pending:
        emit(pending)
        diagnostics.append("UNTERMINATED_CONTINUATION")
    diagnostics.append("SEMANTIC_MAPPING_NOT_ATTEMPTED")
    return LexicalResult(profile, tuple(records), spans, tuple(dict.fromkeys(diagnostics)))
