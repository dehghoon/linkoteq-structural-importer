"""Lossless SAP2000 story/level source inventory for 3D preview.

Source STORY and LEVEL tables are preserved without inventing elevations.
Geometric Z clustering is not treated as a source-defined story.
"""
from __future__ import annotations
from collections import Counter
import re
from .sap2000_geometry import iter_records

def audit_source_levels(archive) -> dict:
    tables = Counter()
    records = []
    for record in iter_records(archive):
        name = record.table.upper()
        if not re.search(r"(?<![A-Z0-9])(?:STORY|STORIES|LEVEL|LEVELS)(?![A-Z0-9])", name):
            continue
        tables[record.table] += 1
        records.append({"table": record.table, "sourceLine": record.line,
                        "sourceFields": list(record.fields),
                        "rawRecord": record.raw, "coreMapped": False})
    return {"sourceHash": archive.sourceHash, "levelTableCounts": dict(tables),
            "sourceRecordCount": len(records), "sourceRecords": records,
            "elevationSemanticsValidated": False,
            "coreLevelMappingValidated": False,
            "geometricLevelsInferred": False, "analysisReady": False}
