"""Import Fidelity supplement for SAP2000 Core v0.6 nonprismatic work.

All source diagnostics remain inspectable. Material identity resolution and
explicit None sections do not authorize an analytical Core model.
"""
from __future__ import annotations
from .sap2000_v06_material_reconciliation import reconcile_tapered_material_diagnostics
from .sap2000_none_sections import audit_none_section_assignments
from .sap2000_nonprismatic_references import audit_nonprismatic_end_sections
from .sap2000_frame_axes import extract_frame_axes
from .sap2000_diaphragms import extract_diaphragms

def build_sap2000_v06_fidelity_supplement(archive, geometry, properties,
                                           partial: dict) -> dict:
    hashes = {archive.sourceHash, geometry.source_hash,
              properties.source_hash, partial.get("sourceHash")}
    if len(hashes) != 1:
        raise ValueError("SOURCE_HASH_MISMATCH")
    materials = reconcile_tapered_material_diagnostics(archive, properties, partial)
    none_sections = audit_none_section_assignments(properties, geometry)
    tapered = audit_nonprismatic_end_sections(archive, properties)
    axes = extract_frame_axes(archive)
    diaphragms = extract_diaphragms(archive)
    if axes.source_hash != archive.sourceHash or diaphragms.source_hash != archive.sourceHash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    return {
        "targetCoreContract": "v0.6.0",
        "sourceHash": archive.sourceHash,
        "originalSourcePreserved": True,
        "originalDiagnostics": list(partial["unresolvedReferences"]),
        "materialIdentityResolution": materials,
        "explicitNoneSectionAssignments": none_sections,
        "nonprismaticSectionDefinitions": tapered,
        "frameLocalAxes": {
            "rotations": [{"frameId": x.frame_id, "angleDegrees": str(x.angle_degrees), "sourceLine": x.source_line} for x in axes.rotations],
            "insertions": [{"frameId": x.frame_id, "fields": list(x.fields), "sourceLine": x.source_line} for x in axes.insertions],
            "diagnostics": list(axes.diagnostics),
            "mappedToCore": False,
        },
        "diaphragmConstraints": {
            "definitions": [{"sourceId": x.source_id, "coordinateSystem": x.coordinate_system, "axis": x.axis, "multiLevel": x.multi_level, "sourceLine": x.source_line} for x in diaphragms.definitions],
            "memberships": [{"jointId": x.joint_id, "diaphragmId": x.diaphragm_id, "sourceLine": x.source_line} for x in diaphragms.memberships],
            "diagnostics": list(diaphragms.diagnostics),
            "mappedToCore": False,
        },
        "engineeringDisposition": {
            "taperedMaterialIdentities": "source-verified",
            "nonprismaticAnalyticalSections": "preserved-not-mapped",
            "explicitNoneAssignments": "preserved-not-substituted",
            "frameAxesAndInsertions": "source-preserved-not-core-mapped",
            "diaphragmConstraints": "source-preserved-not-core-mapped",
            "otherCoreDomains": "not-validated",
        },
        "canonicalCoreValidated": False,
        "analysisReady": False,
        "coreModel": None,
    }
