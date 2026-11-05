"""Fail-closed classification of distributed-load station readiness.

No source record is declared Core-ready merely because its axial offset is
zero. Transverse offsets can alter analysis moments, and missing explicit
fields cannot be silently interpreted as zero.
"""
from __future__ import annotations
from collections import Counter
from .sap2000_axial_insertion_audit import audit_axial_insertion_offsets
from .sap2000_load_stations import audit_distributed_load_stations

def classify_distributed_station_readiness(archive, geometry) -> dict:
    offsets = audit_axial_insertion_offsets(archive, geometry)
    stations = audit_distributed_load_stations(archive, geometry)
    by_frame = {x["frameId"]: x for x in offsets["assignments"]}
    records = []
    counts = Counter()
    for station in stations["records"]:
        frame = by_frame.get(station["frameId"])
        if frame is None:
            reason = "INSERTION_ASSIGNMENT_MISSING"
        elif frame["invalidNumericFields"]:
            reason = "INVALID_INSERTION_FIELD"
        elif frame["nonzeroAxialFields"]:
            reason = "NONZERO_AXIAL_INSERTION_OFFSET"
        elif frame["nonzeroTransverseFields"]:
            reason = "TRANSVERSE_OFFSET_FORCE_MOMENT_EFFECT_UNVERIFIED"
        elif not frame["sourceOffsetFields"]:
            reason = "EXPLICIT_OFFSET_FIELDS_ABSENT"
        else:
            reason = "ZERO_EXPLICIT_OFFSETS_BUT_STATION_SEMANTICS_UNVERIFIED"
        counts[reason] += 1
        records.append({
            "frameId": station["frameId"], "patternId": station["patternId"],
            "sourceLine": station["sourceLine"],
            "geometricStartStationM": station["startStationM"],
            "geometricEndStationM": station["endStationM"],
            "readiness": "PRESERVE_ONLY", "reason": reason,
            "coreStationValidated": False,
        })
    for issue in stations["issues"]:
        counts[issue["reason"]] += 1
    return {"sourceHash": archive.sourceHash, "recordCount": len(records),
            "unresolvedStationCount": len(stations["issues"]),
            "reasonCounts": dict(counts), "records": records,
            "coreReadyCount": 0, "analysisReady": False}
