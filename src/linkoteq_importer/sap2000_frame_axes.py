"""Source-provenanced SAP2000 frame local-axis rotations and insertion assignments.

Angles are source units (SAP2000 angle degrees in this table) and are NOT
transformed into global direction vectors or promoted to Core here.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .preservation import Archive, ArchiveError
from .sap2000_geometry import iter_records, _unique, _number, extract_geometry

@dataclass(frozen=True)
class FrameAxisRotation:
    frame_id: str
    angle_degrees: Decimal
    source_line: int

@dataclass(frozen=True)
class FrameInsertion:
    frame_id: str
    fields: tuple[tuple[str,str], ...]
    source_line: int

@dataclass(frozen=True)
class FrameAxisView:
    rotations: tuple[FrameAxisRotation,...]
    insertions: tuple[FrameInsertion,...]
    diagnostics: tuple[str,...]
    source_hash: str
    mapped_to_core: bool = False

def extract_frame_axes(archive: Archive) -> FrameAxisView:
    rotations,insertions,diagnostics=[],[],[]
    seen_rotations=set()
    seen_insertions=set()
    for record in iter_records(archive):
        if record.table not in ("FRAME LOCAL AXES ASSIGNMENTS 1 - TYPICAL",
                                "FRAME INSERTION POINT ASSIGNMENTS"):
            continue
        f=_unique(record)
        frame=f.get("frame")
        if not frame:
            raise ArchiveError(f"SAP_FRAME_AXIS_MISSING_FRAME:{record.line}")
        if record.table=="FRAME LOCAL AXES ASSIGNMENTS 1 - TYPICAL":
            if frame in seen_rotations:
                diagnostics.append(f"DUPLICATE_FRAME_AXIS_ROTATION:{record.line}:{frame}")
            seen_rotations.add(frame)
            rotations.append(FrameAxisRotation(frame,_number(f,"angle",record.line),record.line))
        else:
            if frame in seen_insertions:
                diagnostics.append(f"DUPLICATE_FRAME_INSERTION:{record.line}:{frame}")
            seen_insertions.add(frame)
            insertions.append(FrameInsertion(frame,record.fields,record.line))
    frame_ids={frame.source_id for frame in extract_geometry(archive).frames}
    for item in rotations:
        if item.frame_id not in frame_ids:
            diagnostics.append(f"FRAME_AXIS_UNKNOWN_FRAME:{item.source_line}:{item.frame_id}")
    for item in insertions:
        if item.frame_id not in frame_ids:
            diagnostics.append(f"FRAME_INSERTION_UNKNOWN_FRAME:{item.source_line}:{item.frame_id}")
    return FrameAxisView(tuple(rotations),tuple(insertions),
                         tuple(diagnostics),archive.sourceHash)
