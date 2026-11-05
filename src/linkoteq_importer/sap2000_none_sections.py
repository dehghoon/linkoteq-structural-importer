"""Source-provenanced SAP2000 'None' frame section assignments.

Treat the literal None as an explicit source assignment, never as an
unknown catalog section to be replaced with a default.
"""
from __future__ import annotations

def audit_none_section_assignments(properties, geometry) -> dict:
    frames = {frame.source_id for frame in geometry.frames}
    records = []
    for assignment in properties.assignments:
        if assignment.section_id.casefold() != "none":
            continue
        records.append({
            "frameId": assignment.frame_id,
            "sourceLine": assignment.source_line,
            "sourceSectionValue": assignment.section_id,
            "frameExists": assignment.frame_id in frames,
            "materialOverride": assignment.material_override,
            "status": "source-explicit-no-section-preserved",
            "coreAnalyticalSectionMapped": False,
        })
    return {
        "sourceHash": properties.source_hash,
        "records": records,
        "count": len(records),
        "mappingStatus": "preserved-not-analysis-ready",
        "analysisReady": False,
        "policy": "never-replace-explicit-none-with-default-section",
    }
