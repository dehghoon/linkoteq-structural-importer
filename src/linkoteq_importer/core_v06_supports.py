"""Map SAP2000 global joint restraints to Core v0.6 support shape.

Only the six source restraint booleans are converted. Local springs,
frame releases and coordinate-dependent actions remain outside this mapping.
"""
from __future__ import annotations

DOFS = ("DX", "DY", "DZ", "RX", "RY", "RZ")

def map_global_restraints_v06(boundaries, geometry) -> dict:
    if boundaries.source_hash != geometry.source_hash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    nodes = {joint.source_id for joint in geometry.joints}
    supports = []
    seen = set()
    diagnostics = []
    for restraint in boundaries.restraints:
        source_id = restraint.joint_id
        if source_id in seen:
            raise ValueError("DUPLICATE_RESTRAINT:" + source_id)
        seen.add(source_id)
        if source_id not in nodes:
            diagnostics.append("UNKNOWN_RESTRAINT_NODE:" + source_id)
            continue
        if len(restraint.fixed) != 6 or any(type(x) is not bool for x in restraint.fixed):
            diagnostics.append("INVALID_RESTRAINT_DOF:" + source_id)
            continue
        supports.append({
            "id": "sap2000:support:" + source_id,
            "nodeId": "sap2000:node:" + source_id,
            "restraints": dict(zip(DOFS, restraint.fixed)),
        })
    return {
        "targetSchemaVersion": "0.6",
        "sourceHash": geometry.source_hash,
        "supports": supports,
        "diagnostics": diagnostics,
        "status": "blocked" if diagnostics else "source-support-subset-unvalidated",
        "canonicalMappingValidated": False,
        "omittedDomains": ["joint-springs", "frame-releases", "support-provenance-in-core"],
    }
