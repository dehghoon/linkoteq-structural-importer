"""Validate SAP2000 source load references without inventing load transforms.

Preserves source-only status until units, directions and Core mapping are verified.
"""
from __future__ import annotations
from collections import Counter
from .sap2000_loads import extract_loads
from .sap2000_advanced_loads import extract_advanced_loads

def audit_sap2000_load_references(archive, geometry) -> dict:
    loads = extract_loads(archive)
    advanced = extract_advanced_loads(archive)
    if any(x != archive.sourceHash for x in (geometry.source_hash, loads.source_hash,
                                              advanced.source_hash)):
        raise ValueError("SOURCE_HASH_MISMATCH")
    joints = {x.source_id for x in geometry.joints}
    frames = {x.source_id for x in geometry.frames}
    patterns = {x.source_id for x in loads.patterns}
    issues = []
    def flag(code, line, ident):
        issues.append({"code": code, "sourceLine": line, "sourceId": ident})
    for force in loads.joint_forces:
        if force.joint_id not in joints:
            flag("UNKNOWN_JOINT_LOAD_TARGET", force.source_line, force.joint_id)
        if force.pattern_id not in patterns:
            flag("UNKNOWN_JOINT_LOAD_PATTERN", force.source_line, force.pattern_id)
        if force.coordinate_system.casefold() != "global":
            flag("JOINT_LOAD_COORDINATE_TRANSFORM_REQUIRED", force.source_line, force.joint_id)
    for distributed in advanced.distributed:
        if distributed.frame_id not in frames:
            flag("UNKNOWN_FRAME_LOAD_TARGET", distributed.source_line, distributed.frame_id)
        if distributed.pattern_id not in patterns:
            flag("UNKNOWN_FRAME_LOAD_PATTERN", distributed.source_line, distributed.pattern_id)
        if distributed.coordinate_system.casefold() != "global":
            flag("FRAME_LOAD_COORDINATE_TRANSFORM_REQUIRED", distributed.source_line,
                 distributed.frame_id)
    return {
        "sourceHash": archive.sourceHash,
        "counts": {
            "patterns": len(loads.patterns),
            "jointForces": len(loads.joint_forces),
            "distributedFrameLoads": len(advanced.distributed),
            "loadCases": len(advanced.cases),
            "loadCombinations": len(advanced.combinations),
        },
        "issues": issues,
        "byCode": dict(Counter(x["code"] for x in issues)),
        "existingParserDiagnostics": list(loads.diagnostics) + list(advanced.diagnostics),
        "mappedToCore": False,
        "unitsVerified": False,
        "analysisReady": False,
    }
