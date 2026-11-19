"""Source-provenanced SAP2000 joint restraints, uncoupled springs and frame releases.

No Core mapping, coordinate transformation or analysis equivalence is implied.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .preservation import Archive, ArchiveError
from .sap2000_geometry import iter_records, _unique, _number

DOFS=("u1","u2","u3","r1","r2","r3")
RELEASES=("pi","v2i","v3i","ti","m2i","m3i","pj","v2j","v3j","tj","m2j","m3j")

@dataclass(frozen=True)
class JointRestraint:
    joint_id: str
    fixed: tuple[bool,...]
    source_line: int

@dataclass(frozen=True)
class JointSpring:
    joint_id: str
    coordinate_system: str
    stiffness: tuple[Decimal,...]
    source_line: int

@dataclass(frozen=True)
class FrameRelease:
    frame_id: str
    released: tuple[bool,...]
    source_line: int

@dataclass(frozen=True)
class BoundaryView:
    restraints: tuple[JointRestraint,...]
    springs: tuple[JointSpring,...]
    releases: tuple[FrameRelease,...]
    diagnostics: tuple[str,...]
    source_hash: str
    mapped_to_core: bool = False

def _yesno(fields,key,line):
    value=fields.get(key)
    if value is None or value.casefold() not in ("yes","no"):
        raise ArchiveError(f"SAP_INVALID_BOOLEAN:{line}:{key}")
    return value.casefold()=="yes"

def extract_boundaries(archive:Archive)->BoundaryView:
    restraints,springs,releases=[],[],[]
    seen_r,seen_s,seen_f=set(),set(),set()
    diagnostics=[]
    for record in iter_records(archive):
        table=record.table
        if table not in ("JOINT RESTRAINT ASSIGNMENTS","JOINT SPRING ASSIGNMENTS 1 - UNCOUPLED",
                         "FRAME RELEASE ASSIGNMENTS 1 - GENERAL"):
            continue
        f=_unique(record)
        if table=="JOINT RESTRAINT ASSIGNMENTS":
            joint=f.get("joint")
            if not joint or joint in seen_r:
                raise ArchiveError(f"SAP_DUPLICATE_OR_MISSING_RESTRAINT:{record.line}")
            seen_r.add(joint)
            restraints.append(JointRestraint(joint,tuple(_yesno(f,d,record.line) for d in DOFS),record.line))
        elif table=="JOINT SPRING ASSIGNMENTS 1 - UNCOUPLED":
            joint=f.get("joint")
            if not joint or joint in seen_s:
                raise ArchiveError(f"SAP_DUPLICATE_OR_MISSING_SPRING:{record.line}")
            seen_s.add(joint)
            system=f.get("coordsys")
            if not system:
                raise ArchiveError(f"SAP_MISSING_SPRING_COORDSYS:{record.line}")
            if system.casefold()!="global":
                diagnostics.append(f"SPRING_LOCAL_AXES_REQUIRE_TRANSFORM:{record.line}:{joint}")
            springs.append(JointSpring(joint,system,tuple(_number(f,d,record.line) for d in DOFS),record.line))
        else:
            frame=f.get("frame")
            if not frame or frame in seen_f:
                raise ArchiveError(f"SAP_DUPLICATE_OR_MISSING_RELEASE:{record.line}")
            seen_f.add(frame)
            releases.append(FrameRelease(frame,tuple(_yesno(f,d,record.line) for d in RELEASES),record.line))
    return BoundaryView(tuple(restraints),tuple(springs),tuple(releases),
                        tuple(diagnostics),archive.sourceHash)
