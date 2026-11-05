"""Conservative audit of SAP2000 frame insertion assignments affecting load stations.

Do not assume an insertion assignment is zero-offset based on presence alone.
Retain every source field and mark source-frame station equivalence unverified
until SAP2000 end-offset semantics are established.
"""
from __future__ import annotations
from collections import Counter
from .sap2000_frame_axes import extract_frame_axes
from .sap2000_advanced_loads import extract_advanced_loads

def audit_load_station_insertion_interactions(archive, geometry) -> dict:
    axes = extract_frame_axes(archive)
    loads = extract_advanced_loads(archive)
    if axes.source_hash != geometry.source_hash or loads.source_hash != geometry.source_hash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    insertions = {}
    for insertion in axes.insertions:
        insertions.setdefault(insertion.frame_id, []).append(insertion)
    affected = []
    for load in loads.distributed:
        for insertion in insertions.get(load.frame_id, []):
            affected.append({
                "frameId": load.frame_id,
                "patternId": load.pattern_id,
                "loadSourceLine": load.source_line,
                "insertionSourceLine": insertion.source_line,
                "insertionSourceFields": list(insertion.fields),
                "disposition": "PRESERVED_PENDING_INSERTION_SEMANTICS",
                "coreStationValidated": False,
            })
    return {
        "sourceHash": archive.sourceHash,
        "insertionAssignmentCount": len(axes.insertions),
        "loadedFramesWithInsertionAssignment": len({x["frameId"] for x in affected}),
        "affectedLoadCount": len({x["loadSourceLine"] for x in affected}),
        "insertionAssignmentsPerFrame": dict(Counter(x.frame_id for x in axes.insertions)),
        "affectedLoadRecords": affected,
        "insertionOffsetsInterpreted": False,
        "coreStationMappingValidated": False,
        "analysisReady": False,
    }
