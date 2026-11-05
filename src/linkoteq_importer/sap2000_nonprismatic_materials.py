"""Resolve nonprismatic member material identity only when both ends agree.

This does not imply uniform-section equivalence or analysis readiness.
"""
from __future__ import annotations
from .sap2000_nonprismatic_references import audit_nonprismatic_end_sections

def resolve_nonprismatic_member_materials(archive, properties, partial: dict) -> dict:
    references = audit_nonprismatic_end_sections(archive, properties)
    by_section = {}
    for segment in references["segments"]:
        by_section.setdefault(segment["nonprismaticSectionId"], []).append(segment)
    resolutions = []
    unresolved = []
    for member in partial["members"]:
        section_id = member.get("sectionId", "").removeprefix("sap2000:section:")
        if section_id not in by_section:
            continue
        segments = by_section[section_id]
        material_ids = [endpoint["materialId"]
                        for segment in segments for endpoint in segment["endpoints"]]
        endpoints = [endpoint for segment in segments for endpoint in segment["endpoints"]]
        if (all(endpoint["sectionFound"] and endpoint["materialFound"]
                for endpoint in endpoints) and
                len(set(material_ids)) == 1 and material_ids[0]):
            resolutions.append({
                "memberId": member["sourceId"],
                "sectionId": section_id,
                "resolvedMaterialId": material_ids[0],
                "sourceSegmentLines": [segment["sourceLine"] for segment in segments],
                "resolution": "source-verified-endpoint-material-consensus",
                "analyticalSectionMapped": False,
            })
        else:
            unresolved.append("NONPRISMATIC_MATERIAL_AMBIGUOUS:" + member["sourceId"] +
                              ":" + section_id)
    return {
        "sourceHash": archive.sourceHash,
        "resolutions": resolutions,
        "unresolved": unresolved,
        "materialIdentityOnly": True,
        "coreAnalyticalSectionMapped": False,
        "analysisReady": False,
    }
