"""Source-frame distance conversion for SAP2000 distributed loads.

Uses source Cartesian geometry and Decimal arithmetic. Does not adjust for
frame insertion offsets or assert that source stationing equals Core stationing.
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from .sap2000_advanced_loads import extract_advanced_loads

def audit_distributed_load_stations(archive, geometry) -> dict:
    if archive.sourceHash != geometry.source_hash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    nodes = {x.source_id: x for x in geometry.joints}
    frames = {x.source_id: x for x in geometry.frames}
    records, issues = [], []
    with localcontext() as ctx:
        ctx.prec = 34
        for load in extract_advanced_loads(archive).distributed:
            frame = frames.get(load.frame_id)
            if frame is None or frame.joint_i not in nodes or frame.joint_j not in nodes:
                issues.append({"sourceLine": load.source_line, "frameId": load.frame_id,
                               "reason": "FRAME_OR_ENDPOINT_UNRESOLVED"})
                continue
            a, b = nodes[frame.joint_i], nodes[frame.joint_j]
            length = sum((getattr(b, k) - getattr(a, k)) ** 2 for k in ("x", "y", "z")).sqrt()
            if length == 0:
                issues.append({"sourceLine": load.source_line, "frameId": load.frame_id,
                               "reason": "ZERO_LENGTH_FRAME"})
                continue
            relative = load.distance_type.casefold() == "reldist"
            absolute = load.distance_type.casefold() == "absdist"
            if not (relative or absolute):
                issues.append({"sourceLine": load.source_line, "frameId": load.frame_id,
                               "reason": "UNKNOWN_DISTANCE_TYPE"})
                continue
            x1 = load.start * length if relative else load.start
            x2 = load.end * length if relative else load.end
            if not (Decimal(0) <= x1 <= x2 <= length):
                issues.append({"sourceLine": load.source_line, "frameId": load.frame_id,
                               "reason": "DISTANCE_OUTSIDE_GEOMETRIC_MEMBER"})
                continue
            records.append({"frameId": load.frame_id, "patternId": load.pattern_id,
                            "sourceLine": load.source_line,
                            "sourceDistanceType": load.distance_type,
                            "sourceStart": str(load.start), "sourceEnd": str(load.end),
                            "geometricLengthM": str(length),
                            "startStationM": str(x1), "endStationM": str(x2),
                            "insertionOffsetsApplied": False,
                            "coreStationMappingValidated": False})
    return {"sourceHash": archive.sourceHash, "records": records, "issues": issues,
            "recordCount": len(records), "unresolvedCount": len(issues),
            "offsetAware": False, "analysisReady": False}
