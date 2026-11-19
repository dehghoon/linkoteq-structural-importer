"""Audit SAP2000 tapered-section source tables without inferred properties.

Extract all raw key/value fields from tables naming tapered or nonprismatic
frame sections, with source line numbers and original archive hash.
"""
from __future__ import annotations
from .sap2000_geometry import iter_records

def audit_tapered_source(archive, *, section_id: str = "Tapered Beam") -> dict:
    records = []
    for record in iter_records(archive):
        table = record.table
        if "FRAME SECTION" not in table:
            continue
        fields = list(record.fields)
        values = [value for _, value in fields]
        is_tapered_table = any(word in table.upper()
                               for word in ("NONPRISMATIC", "TAPERED", "VARIABLE"))
        references_section = section_id in values
        if not (is_tapered_table or references_section):
            continue
        records.append({
            "table": table,
            "sourceLine": record.line,
            "fields": fields,
            "referencesTargetSection": references_section,
        })
    return {
        "sourceHash": archive.sourceHash,
        "targetSectionId": section_id,
        "records": records,
        "recordCount": len(records),
        "candidateTables": sorted({r["table"] for r in records}),
        "mappedToCore": False,
        "analysisReady": False,
        "policy": "preserve-raw-tapered-definition-no-inferred-section-or-material",
    }
