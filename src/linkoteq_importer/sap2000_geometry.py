"""Source-provenanced SAP2000 tabular geometry extraction (not Core mapping).

Preserves every original byte in Archive; this view extracts only joint/frame geometry.
Unknown tables remain in the source archive, never silently discarded.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re

from .preservation import Archive, ArchiveError

_HEADER = re.compile(r'^TABLE:\s*"([^"]+)"$', re.I)
_FIELD = re.compile(r'([A-Za-z][A-Za-z0-9_]*)\s*=\s*(?:"([^"]*)"|([^\s"]+))')
_NUM = re.compile(r'^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$')


@dataclass(frozen=True)
class SourceRecord:
    table: str
    line: int
    fields: tuple[tuple[str, str], ...]
    raw: str


@dataclass(frozen=True)
class Joint:
    source_id: str
    x: Decimal
    y: Decimal
    z: Decimal
    source_line: int


@dataclass(frozen=True)
class Frame:
    source_id: str
    joint_i: str
    joint_j: str
    source_line: int


@dataclass(frozen=True)
class GeometryView:
    joints: tuple[Joint, ...]
    frames: tuple[Frame, ...]
    source_hash: str
    declared_units: str | None
    diagnostics: tuple[str, ...]
    mapped_to_core: bool = False


def iter_records(archive: Archive):
    text = archive.retrieve().decode("utf-8-sig")
    table = None
    parts = []
    first_line = 0
    for line_no, original in enumerate(text.splitlines(), 1):
        stripped = original.strip()
        match = _HEADER.fullmatch(stripped)
        if match:
            if parts:
                raise ArchiveError(f"SAP_UNTERMINATED_CONTINUATION:{first_line}")
            table = match.group(1)
            continue
        if not stripped or stripped == "END TABLE DATA":
            if parts:
                raise ArchiveError(f"SAP_UNTERMINATED_CONTINUATION:{first_line}")
            continue
        if table is None:
            continue  # Source preamble retained in Archive.
        if not parts:
            first_line = line_no
        continued = stripped.endswith("_")
        parts.append(stripped[:-1].rstrip() if continued else stripped)
        if continued:
            continue
        raw = " ".join(parts)
        fields = tuple((m.group(1), m.group(2) if m.group(2) is not None else m.group(3))
                       for m in _FIELD.finditer(raw))
        yield SourceRecord(table, first_line, fields, raw)
        parts.clear()
    if parts:
        raise ArchiveError(f"SAP_UNTERMINATED_CONTINUATION:{first_line}")


def _unique(record: SourceRecord) -> dict[str, str]:
    fields = {}
    for key, value in record.fields:
        key = key.casefold()
        if key in fields:
            raise ArchiveError(f"SAP_DUPLICATE_FIELD:{record.line}:{key}")
        fields[key] = value
    return fields


def _number(fields: dict[str, str], key: str, line: int) -> Decimal:
    raw = fields.get(key)
    if raw is None or not _NUM.fullmatch(raw):
        raise ArchiveError(f"SAP_INVALID_COORDINATE:{line}:{key}")
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ArchiveError(f"SAP_INVALID_COORDINATE:{line}:{key}") from exc
    if not value.is_finite():
        raise ArchiveError(f"SAP_NONFINITE_COORDINATE:{line}:{key}")
    return value


def extract_geometry(archive: Archive) -> GeometryView:
    joints = []
    frames = []
    joint_ids = set()
    frame_ids = set()
    units = None
    diagnostics = []
    for record in iter_records(archive):
        f = _unique(record)
        if record.table == "PROGRAM CONTROL":
            current = f.get("currunits")
            if current:
                if units is not None and current != units:
                    diagnostics.append(f"CONFLICTING_DECLARED_UNITS:{record.line}")
                units = current
        elif record.table == "JOINT COORDINATES":
            source_id = f.get("joint")
            if not source_id:
                raise ArchiveError(f"SAP_MISSING_JOINT_ID:{record.line}")
            if source_id in joint_ids:
                raise ArchiveError(f"SAP_DUPLICATE_JOINT_ID:{record.line}:{source_id}")
            joint_ids.add(source_id)
            if f.get("coordtype", "Cartesian").casefold() != "cartesian" or f.get("coordsys", "GLOBAL").casefold() != "global":
                raise ArchiveError(f"SAP_UNSUPPORTED_JOINT_COORDINATES:{record.line}")
            joints.append(Joint(source_id, _number(f,"xorr",record.line),
                                _number(f,"y",record.line), _number(f,"z",record.line),
                                record.line))
        elif record.table == "CONNECTIVITY - FRAME":
            source_id, a, b = f.get("frame"), f.get("jointi"), f.get("jointj")
            if not all((source_id, a, b)):
                raise ArchiveError(f"SAP_INCOMPLETE_FRAME:{record.line}")
            if source_id in frame_ids:
                raise ArchiveError(f"SAP_DUPLICATE_FRAME_ID:{record.line}:{source_id}")
            frame_ids.add(source_id)
            frames.append(Frame(source_id,a,b,record.line))
    for frame in frames:
        if frame.joint_i not in joint_ids or frame.joint_j not in joint_ids:
            diagnostics.append(f"UNRESOLVED_FRAME_JOINT:{frame.source_line}:{frame.source_id}")
    if units is None:
        diagnostics.append("UNDECLARED_SOURCE_UNITS")
    return GeometryView(tuple(joints),tuple(frames),archive.sourceHash,units,
                        tuple(diagnostics))
