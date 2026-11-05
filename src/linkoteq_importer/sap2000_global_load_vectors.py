"""Verified GLOBAL Y/Z SAP2000 distributed-force SI vector candidates.

Gravity direction is intentionally excluded until source sign conventions
are independently verified. No Core load object is emitted.
"""
from __future__ import annotations
from decimal import Decimal
from .sap2000_advanced_loads import extract_advanced_loads
from .sap2000_load_units import audit_sap2000_load_units

def project_global_distributed_vectors(archive, geometry) -> dict:
    units = audit_sap2000_load_units(archive, geometry)
    if units["distinctDeclarations"] != ["KN, m, C"] or units["issues"]:
        raise ValueError("UNVERIFIED_SAP_LOAD_UNITS")
    loads = extract_advanced_loads(archive)
    vectors, deferred = [], []
    basis = {"X": 0, "Y": 1, "Z": 2}
    for load in loads.distributed:
        direction = load.direction.upper()
        if (load.coordinate_system.upper() != "GLOBAL"
                or load.load_type.casefold() != "force"
                or direction not in basis):
            deferred.append({"frameId": load.frame_id, "patternId": load.pattern_id,
                             "sourceLine": load.source_line,
                             "direction": load.direction,
                             "coordinateSystem": load.coordinate_system,
                             "reason": "DIRECTION_OR_LOAD_TYPE_REQUIRES_SEMANTIC_VERIFICATION"})
            continue
        def vector(value):
            values = [Decimal(0), Decimal(0), Decimal(0)]
            values[basis[direction]] = value * Decimal(1000)
            return [str(x) for x in values]
        vectors.append({"frameId": load.frame_id, "patternId": load.pattern_id,
                        "sourceLine": load.source_line, "sourceDirection": load.direction,
                        "sourceDistanceType": load.distance_type,
                        "sourceStart": str(load.start), "sourceEnd": str(load.end),
                        "startVectorNPerM": vector(load.magnitude_start),
                        "endVectorNPerM": vector(load.magnitude_end),
                        "sourceCoordinateSystem": load.coordinate_system,
                        "coreMappingValidated": False})
    return {"sourceHash": archive.sourceHash, "vectorCandidates": vectors,
            "deferredLoads": deferred, "mappedToCore": False,
            "gravitySignVerified": False, "analysisReady": False}
