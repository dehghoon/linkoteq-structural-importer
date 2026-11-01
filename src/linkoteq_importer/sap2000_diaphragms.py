"""SAP2000 diaphragm constraints and joint memberships: source evidence only.

Area membrane section names are not converted to rigid diaphragms.
Unresolved memberships remain diagnostics; archive retains all original bytes.
"""
from __future__ import annotations
from dataclasses import dataclass
from .preservation import Archive, ArchiveError
from .sap2000_geometry import iter_records, _unique

@dataclass(frozen=True)
class DiaphragmDefinition:
    source_id: str
    coordinate_system: str | None
    axis: str | None
    multi_level: str | None
    source_line: int

@dataclass(frozen=True)
class DiaphragmMembership:
    joint_id: str
    diaphragm_id: str
    source_line: int

@dataclass(frozen=True)
class DiaphragmView:
    definitions: tuple[DiaphragmDefinition,...]
    memberships: tuple[DiaphragmMembership,...]
    diagnostics: tuple[str,...]
    source_hash: str
    mapped_to_core: bool = False

def extract_diaphragms(archive: Archive) -> DiaphragmView:
    definitions=[]
    memberships=[]
    diagnostics=[]
    seen=set()
    for record in iter_records(archive):
        if record.table not in ("CONSTRAINT DEFINITIONS - DIAPHRAGM",
                                "JOINT CONSTRAINT ASSIGNMENTS"):
            continue
        fields=_unique(record)
        if record.table=="CONSTRAINT DEFINITIONS - DIAPHRAGM":
            name=fields.get("name")
            if not name or name in seen:
                raise ArchiveError(f"SAP_DUPLICATE_OR_MISSING_DIAPHRAGM:{record.line}")
            seen.add(name)
            definitions.append(DiaphragmDefinition(
                name,fields.get("coordsys"),fields.get("axis"),
                fields.get("multilevel"),record.line))
            if not fields.get("coordsys") or not fields.get("axis"):
                diagnostics.append(f"DIAPHRAGM_AXIS_OR_COORDSYS_UNVERIFIED:{record.line}:{name}")
        else:
            joint=fields.get("joint")
            constraint=fields.get("constraint")
            if not joint or not constraint:
                raise ArchiveError(f"SAP_INCOMPLETE_JOINT_CONSTRAINT:{record.line}")
            memberships.append(DiaphragmMembership(joint,constraint,record.line))
    for member in memberships:
        if member.diaphragm_id not in seen:
            diagnostics.append(f"JOINT_CONSTRAINT_NOT_DIAPHRAGM_DEFINITION:{member.source_line}:{member.diaphragm_id}")
    return DiaphragmView(tuple(definitions),tuple(memberships),
                         tuple(diagnostics),archive.sourceHash)
