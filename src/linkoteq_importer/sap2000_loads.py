"""Source-only SAP2000 load patterns and nodal force/moment assignments."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .preservation import Archive, ArchiveError
from .sap2000_geometry import iter_records, _unique, _number

@dataclass(frozen=True)
class LoadPattern:
    source_id: str
    design_type: str | None
    self_weight_multiplier: Decimal
    source_line: int

@dataclass(frozen=True)
class JointForce:
    joint_id: str
    pattern_id: str
    coordinate_system: str
    components: tuple[Decimal,...]
    source_line: int

@dataclass(frozen=True)
class LoadView:
    patterns: tuple[LoadPattern,...]
    joint_forces: tuple[JointForce,...]
    diagnostics: tuple[str,...]
    source_hash: str
    mapped_to_core: bool = False

def extract_loads(archive:Archive)->LoadView:
    patterns,forces=[],[]
    ids=set()
    diagnostics=[]
    for record in iter_records(archive):
        if record.table not in ("LOAD PATTERN DEFINITIONS","JOINT LOADS - FORCE"):
            continue
        f=_unique(record)
        if record.table=="LOAD PATTERN DEFINITIONS":
            ident=f.get("loadpat")
            if not ident or ident in ids:
                raise ArchiveError(f"SAP_DUPLICATE_OR_MISSING_LOAD_PATTERN:{record.line}")
            ids.add(ident)
            patterns.append(LoadPattern(ident,f.get("designtype"),_number(f,"selfwtmult",record.line),record.line))
        else:
            joint,pattern,system=f.get("joint"),f.get("loadpat"),f.get("coordsys")
            if not joint or not pattern or not system:
                raise ArchiveError(f"SAP_INCOMPLETE_JOINT_FORCE:{record.line}")
            if system.casefold()!="global":
                diagnostics.append(f"JOINT_FORCE_NON_GLOBAL_COORDSYS:{record.line}:{joint}")
            forces.append(JointForce(joint,pattern,system,
                                    tuple(_number(f,d,record.line) for d in ("f1","f2","f3","m1","m2","m3")),
                                    record.line))
    for force in forces:
        if force.pattern_id not in ids:
            diagnostics.append(f"UNKNOWN_LOAD_PATTERN:{force.source_line}:{force.pattern_id}")
    return LoadView(tuple(patterns),tuple(forces),tuple(diagnostics),archive.sourceHash)
