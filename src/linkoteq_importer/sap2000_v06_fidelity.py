"""Import Fidelity supplement for SAP2000 Core v0.6 nonprismatic work.

All source diagnostics remain inspectable. Material identity resolution and
explicit None sections do not authorize an analytical Core model.
"""
from __future__ import annotations
from .sap2000_v06_material_reconciliation import reconcile_tapered_material_diagnostics
from .sap2000_none_sections import audit_none_section_assignments
from .sap2000_nonprismatic_references import audit_nonprismatic_end_sections

def build_sap2000_v06_fidelity_supplement(archive, geometry, properties,
                                           partial: dict) -> dict:
    hashes = {archive.sourceHash, geometry.source_hash,
              properties.source_hash, partial.get("sourceHash")}
    if len(hashes) != 1:
        raise ValueError("SOURCE_HASH_MISMATCH")
    materials = reconcile_tapered_material_diagnostics(archive, properties, partial)
    none_sections = audit_none_section_assignments(properties, geometry)
    tapered = audit_nonprismatic_end_sections(archive, properties)
    return {
        "targetCoreContract": "v0.6.0",
        "sourceHash": archive.sourceHash,
        "originalSourcePreserved": True,
        "originalDiagnostics": list(partial["unresolvedReferences"]),
        "materialIdentityResolution": materials,
        "explicitNoneSectionAssignments": none_sections,
        "nonprismaticSectionDefinitions": tapered,
        "engineeringDisposition": {
            "taperedMaterialIdentities": "source-verified",
            "nonprismaticAnalyticalSections": "preserved-not-mapped",
            "explicitNoneAssignments": "preserved-not-substituted",
            "otherCoreDomains": "not-validated",
        },
        "canonicalCoreValidated": False,
        "analysisReady": False,
        "coreModel": None,
    }
