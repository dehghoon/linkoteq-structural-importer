"""Trace unresolved SAP material references back to original frame assignments.

Diagnostic-only: never infer a missing section material or substitute a
catalog default. Report source line, section, override and raw section field.
"""
from __future__ import annotations
from collections import Counter

def audit_material_origins(properties, unresolved_references) -> dict:
    assignments = {a.frame_id: a for a in properties.assignments}
    sections = {s.source_id: s for s in properties.sections}
    records = []
    for diagnostic in unresolved_references:
        if not diagnostic.startswith("UNRESOLVED_MATERIAL:"):
            continue
        _, frame_id, declared = diagnostic.split(":", 2)
        assignment = assignments.get(frame_id)
        section = sections.get(assignment.section_id) if assignment else None
        section_fields = {key.casefold(): value for key, value in section.fields} if section else {}
        records.append({
            "frameId": frame_id,
            "sectionId": assignment.section_id if assignment else None,
            "assignmentSourceLine": assignment.source_line if assignment else None,
            "sectionSourceLine": section.source_line if section else None,
            "materialOverride": assignment.material_override if assignment else None,
            "sectionMaterialField": section_fields.get("material"),
            "declaredUnresolvedMaterial": declared,
            "resolution": "not-mapped-no-substitution",
        })
    counts = Counter((r["sectionId"], r["sectionMaterialField"], r["materialOverride"])
                     for r in records)
    return {
        "totalUnresolvedFrames": len(records),
        "bySourceSection": [
            {"sectionId": section, "sectionMaterialField": material,
             "materialOverride": override, "frameCount": count}
            for (section, material, override), count in
            sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))
        ],
        "records": records,
        "policy": "no-silent-material-substitution",
    }
