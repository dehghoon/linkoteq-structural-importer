"""Consolidate SAP2000 Core v0.6 subset gates without overstating readiness.

The geometry/property candidate is blocked when engineering references are
unresolved. Independently mapped supports and releases remain inspectable;
they must not be merged into an invalid canonical model.
"""
from __future__ import annotations
from .core_v06_candidate import project_geometry_properties_v06
from .core_v06_supports import map_global_restraints_v06
from .core_v06_releases import map_binary_frame_releases_v06
from .core_v06_blockers import classify_blockers
from .sap2000_v06_fidelity import build_sap2000_v06_fidelity_supplement

def build_sap2000_v06_gate_report(partial: dict, geometry, boundaries, *,
                                  project_id: str, archive=None, properties=None) -> dict:
    if partial.get("sourceHash") != geometry.source_hash:
        raise ValueError("PARTIAL_SOURCE_HASH_MISMATCH")
    if boundaries.source_hash != geometry.source_hash:
        raise ValueError("BOUNDARY_SOURCE_HASH_MISMATCH")
    candidate = project_geometry_properties_v06(partial, project_id=project_id)
    supports = map_global_restraints_v06(boundaries, geometry)
    releases = map_binary_frame_releases_v06(boundaries, geometry)
    diagnostics = list(candidate.get("diagnostics", []))
    diagnostics.extend(supports["diagnostics"])
    diagnostics.extend(releases["diagnostics"])
    blockers = classify_blockers(diagnostics)
    if (archive is None) != (properties is None):
        raise ValueError("FIDELITY_REQUIRES_ARCHIVE_AND_PROPERTIES")
    fidelity = (build_sap2000_v06_fidelity_supplement(archive, geometry, properties, partial)
                if archive is not None else None)
    return {
        "importFidelity": fidelity,
        "targetSchemaVersion": "0.6",
        "sourceHash": geometry.source_hash,
        "status": "blocked" if candidate["status"] == "blocked" or blockers["unresolved"]
                  else "candidate-unvalidated",
        "canonicalMappingValidated": False,
        "analysisReady": False,
        "coreModel": None,
        "geometryProperties": candidate,
        "sourceSupportMapping": supports,
        "sourceReleaseMapping": releases,
        "blockers": blockers,
        "counts": {
            "sourceNodes": len(geometry.joints),
            "sourceMembers": len(geometry.frames),
            "mappedSupports": len(supports["supports"]),
            "mappedBinaryFrameReleases": len(releases["members"]),
        },
        "preservationPolicy": "original-source-archive-and-unsupported-fields-retained",
    }
