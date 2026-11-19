"""Lossless SAP2000 grid-table inventory for source preview handoff.

SAP table variants and coordinate semantics are not assumed. All source
grid-related rows are retained, including unrecognized vendor fields.
"""
from __future__ import annotations
from collections import Counter
from .sap2000_geometry import iter_records

def audit_source_grids(archive) -> dict:
    rows = []
    tables = Counter()
    for record in iter_records(archive):
        if "GRID" not in record.table.upper():
            continue
        tables[record.table] += 1
        rows.append({"table": record.table, "sourceLine": record.line,
                     "sourceFields": list(record.fields), "rawRecord": record.raw,
                     "coreMapped": False})
    return {"sourceHash": archive.sourceHash, "gridTableCounts": dict(tables),
            "sourceRecordCount": len(rows), "sourceRecords": rows,
            "coordinateSemanticsValidated": False,
            "coreGridMappingValidated": False,
            "analysisReady": False}
