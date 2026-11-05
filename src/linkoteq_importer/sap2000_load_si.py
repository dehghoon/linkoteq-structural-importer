"""Explicit SAP2000 kN,m load magnitudes to SI with provenance.

Only the exact verified kN,m source declaration is accepted. Source
components and directions are preserved; this does not rotate local loads
or produce Core load objects.
"""
from __future__ import annotations
from decimal import Decimal
from .sap2000_loads import extract_loads
from .sap2000_advanced_loads import extract_advanced_loads
from .sap2000_load_units import audit_sap2000_load_units

def convert_sap2000_kn_m_load_magnitudes(archive, geometry) -> dict:
    audit = audit_sap2000_load_units(archive, geometry)
    if audit["distinctDeclarations"] != ["KN, m, C"] or audit["issues"]:
        raise ValueError("UNVERIFIED_SAP_LOAD_UNITS")
    loads = extract_loads(archive)
    advanced = extract_advanced_loads(archive)
    factor = Decimal("1000")
    nodal = []
    for x in loads.joint_forces:
        nodal.append({
            "jointId": x.joint_id, "patternId": x.pattern_id,
            "sourceCoordinateSystem": x.coordinate_system,
            "sourceComponents": [str(v) for v in x.components],
            "siComponents": [str(v * factor) for v in x.components],
            "componentUnits": ["N", "N", "N", "N*m", "N*m", "N*m"],
            "sourceLine": x.source_line, "directionTransformed": False,
        })
    distributed = []
    for x in advanced.distributed:
        distributed.append({
            "frameId": x.frame_id, "patternId": x.pattern_id,
            "sourceCoordinateSystem": x.coordinate_system,
            "sourceDirection": x.direction, "sourceLoadType": x.load_type,
            "sourceDistanceType": x.distance_type,
            "sourceStart": str(x.start), "sourceEnd": str(x.end),
            "sourceMagnitudes": [str(x.magnitude_start), str(x.magnitude_end)],
            "siMagnitudeCandidates": [str(x.magnitude_start * factor),
                                      str(x.magnitude_end * factor)],
            "magnitudeUnit": "N/m" if x.load_type.casefold() == "force" else None,
            "sourceLine": x.source_line, "directionTransformed": False,
            "coreMappingValidated": False,
        })
    return {
        "sourceHash": archive.sourceHash,
        "sourceUnits": "KN, m, C",
        "nodalLoadsSI": nodal,
        "distributedMagnitudeCandidatesSI": distributed,
        "forceScale": "1000", "momentScale": "1000",
        "distributedForcePerLengthScale": "1000",
        "distributedNonForceTypesValidated": False,
        "localDirectionTransformsValidated": False,
        "coreMappingValidated": False,
        "analysisReady": False,
    }
