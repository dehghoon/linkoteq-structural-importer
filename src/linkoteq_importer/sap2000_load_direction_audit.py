"""Classify SAP2000 distributed load coordinate and distance semantics.

No unsupported local-axis direction is silently promoted to a global Core
vector. Source record identifiers, line numbers and directions remain visible.
"""
from __future__ import annotations
from collections import Counter
from .sap2000_advanced_loads import extract_advanced_loads

def audit_distributed_load_semantics(archive, geometry) -> dict:
    view = extract_advanced_loads(archive)
    if view.source_hash != geometry.source_hash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    records = []
    for x in view.distributed:
        global_coords = x.coordinate_system.casefold() == "global"
        relative = x.distance_type.casefold() == "reldist"
        absolute = x.distance_type.casefold() == "absdist"
        distance_valid = x.start <= x.end and (not relative or
                          (0 <= x.start <= 1 and 0 <= x.end <= 1))
        issues = []
        if not global_coords:
            issues.append("LOCAL_OR_CUSTOM_COORDINATE_TRANSFORM_REQUIRED")
        if not (relative or absolute):
            issues.append("UNKNOWN_DISTANCE_CONVENTION")
        if not distance_valid:
            issues.append("INVALID_DISTANCE_RANGE")
        if x.load_type.casefold() != "force":
            issues.append("NON_FORCE_DISTRIBUTED_TYPE_NOT_VERIFIED")
        records.append({
            "frameId": x.frame_id, "patternId": x.pattern_id,
            "sourceLine": x.source_line, "coordinateSystem": x.coordinate_system,
            "direction": x.direction, "distanceType": x.distance_type,
            "loadType": x.load_type, "issues": issues,
            "coreVectorValidated": False,
        })
    return {
        "sourceHash": archive.sourceHash,
        "recordCount": len(records),
        "byCoordinateSystem": dict(Counter(x["coordinateSystem"] for x in records)),
        "byDirection": dict(Counter(x["direction"] for x in records)),
        "byDistanceType": dict(Counter(x["distanceType"] for x in records)),
        "byLoadType": dict(Counter(x["loadType"] for x in records)),
        "issueCounts": dict(Counter(issue for x in records for issue in x["issues"])),
        "records": records,
        "globalVectorMappingValidated": False,
        "analysisReady": False,
    }
