"""Reconcile SAP2000 material diagnostics with verified tapered endpoints.

Retain the original diagnostic list unchanged for auditability. A resolved
material identity is NOT a resolved nonprismatic analytical section.
"""
from __future__ import annotations
from .sap2000_nonprismatic_materials import resolve_nonprismatic_member_materials

def reconcile_tapered_material_diagnostics(archive, properties, partial: dict) -> dict:
    resolution = resolve_nonprismatic_member_materials(archive, properties, partial)
    resolved = {item["memberId"]: item for item in resolution["resolutions"]}
    original = list(partial["unresolvedReferences"])
    resolved_diagnostics = []
    outstanding = []
    for diagnostic in original:
        if diagnostic.startswith("UNRESOLVED_MATERIAL:"):
            _, frame_id, declared = diagnostic.split(":", 2)
            match = resolved.get(frame_id)
            if match and not declared:
                resolved_diagnostics.append({
                    "originalDiagnostic": diagnostic,
                    "memberId": frame_id,
                    "materialId": match["resolvedMaterialId"],
                    "sourceSegmentLines": match["sourceSegmentLines"],
                    "status": "material-identity-resolved-only",
                })
                continue
        outstanding.append(diagnostic)
    return {
        "sourceHash": archive.sourceHash,
        "originalUnresolvedReferences": original,
        "resolvedMaterialReferences": resolved_diagnostics,
        "outstandingUnresolvedReferences": outstanding,
        "originalUnresolvedCount": len(original),
        "resolvedMaterialCount": len(resolved_diagnostics),
        "remainingReferenceCount": len(outstanding),
        "nonprismaticSectionStatus": "preserved-extension-not-analytical",
        "analysisReady": False,
        "canonicalCoreValidated": False,
    }
