"""Preserve nonprismatic SAP2000 frame-section segments as a source extension.

Do not collapse a tapered member into a uniform section. Segment lengths,
start/end section names, interpolation modes, and source lines remain raw.
"""
from __future__ import annotations
from .sap2000_geometry import iter_records

TABLE = "FRAME SECTION PROPERTIES 05 - NONPRISMATIC"

def extract_nonprismatic_segments(archive) -> dict:
    segments = []
    for record in iter_records(archive):
        if record.table != TABLE:
            continue
        fields = list(record.fields)
        segments.append({
            "sourceLine": record.line,
            "fields": fields,
            "sourceFieldNames": [key for key, _ in fields],
        })
    return {
        "sourceHash": archive.sourceHash,
        "table": TABLE,
        "segments": segments,
        "segmentCount": len(segments),
        "mappingStatus": "preserved-extension",
        "mappedToCore": False,
        "analysisReady": False,
        "warnings": [
            "NONPRISMATIC_SEGMENT_REQUIRES_SECTION_REFERENCE_AND_UNIT_VALIDATION",
            "NO_UNIFORM_SECTION_SUBSTITUTION",
        ],
    }
