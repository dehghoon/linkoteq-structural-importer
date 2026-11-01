"""Read-only engineering reference audit for SAP2000 source views.

Does not modify or map records. Every problem is a diagnostic; no silent repair.
"""
from __future__ import annotations
from dataclasses import dataclass
from .preservation import Archive
from .sap2000_geometry import extract_geometry
from .sap2000_boundary import extract_boundaries
from .sap2000_loads import extract_loads
from .sap2000_advanced_loads import extract_advanced_loads
from .sap2000_diaphragms import extract_diaphragms

@dataclass(frozen=True)
class ReferenceAudit:
    diagnostics: tuple[str, ...]
    counts: dict[str,int]
    source_hash: str
    mapped_to_core: bool = False

def audit_references(archive: Archive) -> ReferenceAudit:
    geometry=extract_geometry(archive)
    boundary=extract_boundaries(archive)
    loads=extract_loads(archive)
    advanced=extract_advanced_loads(archive)
    diaphragms=extract_diaphragms(archive)
    joints={x.source_id for x in geometry.joints}
    frames={x.source_id for x in geometry.frames}
    patterns={x.source_id for x in loads.patterns}
    diagnostics=[]
    for item in boundary.restraints:
        if item.joint_id not in joints:
            diagnostics.append(f"RESTRAINT_UNKNOWN_JOINT:{item.source_line}:{item.joint_id}")
    for item in boundary.springs:
        if item.joint_id not in joints:
            diagnostics.append(f"SPRING_UNKNOWN_JOINT:{item.source_line}:{item.joint_id}")
    for item in boundary.releases:
        if item.frame_id not in frames:
            diagnostics.append(f"RELEASE_UNKNOWN_FRAME:{item.source_line}:{item.frame_id}")
    for item in loads.joint_forces:
        if item.joint_id not in joints:
            diagnostics.append(f"JOINT_LOAD_UNKNOWN_JOINT:{item.source_line}:{item.joint_id}")
        if item.pattern_id not in patterns:
            diagnostics.append(f"JOINT_LOAD_UNKNOWN_PATTERN:{item.source_line}:{item.pattern_id}")
    for item in advanced.distributed:
        if item.frame_id not in frames:
            diagnostics.append(f"FRAME_LOAD_UNKNOWN_FRAME:{item.source_line}:{item.frame_id}")
        if item.pattern_id not in patterns:
            diagnostics.append(f"FRAME_LOAD_UNKNOWN_PATTERN:{item.source_line}:{item.pattern_id}")
    for item in diaphragms.memberships:
        if item.joint_id not in joints:
            diagnostics.append(f"DIAPHRAGM_UNKNOWN_JOINT:{item.source_line}:{item.joint_id}")
    counts={"nodes":len(joints),"frames":len(frames),"restraints":len(boundary.restraints),
            "springs":len(boundary.springs),"releases":len(boundary.releases),
            "nodalLoads":len(loads.joint_forces),"distributedFrameLoads":len(advanced.distributed),
            "diaphragmMemberships":len(diaphragms.memberships)}
    return ReferenceAudit(tuple(diagnostics),counts,archive.sourceHash)
