"""Resolve nonprismatic endpoint section references, never flatten geometry.

This is a source reference audit, not a Core analytical section mapping.
"""
from __future__ import annotations
from collections import Counter
from .sap2000_nonprismatic import extract_nonprismatic_segments

def audit_nonprismatic_end_sections(archive, properties) -> dict:
    segments = extract_nonprismatic_segments(archive)
    sections = {entry.source_id: entry for entry in properties.sections}
    materials = {entry.source_id for entry in properties.materials}
    records = []
    issues = []
    for segment in segments["segments"]:
        fields = {key.casefold(): value for key, value in segment["fields"]}
        section_id = fields.get("sectionname")
        endpoints = []
        for role, key in (("start", "startsect"), ("end", "endsect")):
            name = fields.get(key)
            section = sections.get(name) if name else None
            section_fields = ({k.casefold(): v for k, v in section.fields}
                              if section else {})
            material = section_fields.get("material")
            resolved = section is not None and material in materials
            if not name or section is None:
                issues.append("NONPRISMATIC_UNKNOWN_" + role.upper() + "_SECTION:" +
                              str(segment["sourceLine"]) + ":" + str(name))
            elif not resolved:
                issues.append("NONPRISMATIC_UNRESOLVED_" + role.upper() + "_MATERIAL:" +
                              str(segment["sourceLine"]) + ":" + str(material))
            endpoints.append({
                "role": role,
                "sectionId": name,
                "sectionSourceLine": section.source_line if section else None,
                "materialId": material,
                "sectionFound": section is not None,
                "materialFound": material in materials if material else False,
            })
        records.append({
            "sourceLine": segment["sourceLine"],
            "nonprismaticSectionId": section_id,
            "endpoints": endpoints,
            "lengthType": fields.get("lengthtype"),
            "absoluteLengthSource": fields.get("abslength"),
            "ei33Variation": fields.get("ei33var"),
            "ei22Variation": fields.get("ei22var"),
            "rawFields": segment["fields"],
            "mappingStatus": "preserved-extension",
        })
    return {
        "sourceHash": archive.sourceHash,
        "segments": records,
        "diagnostics": issues,
        "diagnosticCounts": dict(Counter(issue.split(":", 1)[0] for issue in issues)),
        "coreAnalyticalSectionMapped": False,
        "analysisReady": False,
    }
