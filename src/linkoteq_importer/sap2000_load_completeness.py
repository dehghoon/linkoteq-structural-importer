"""Reconcile every raw SAP2000 distributed-load row against parsed source view.

Rows skipped for unsupported distance/magnitude formats remain losslessly
archived, but must be explicitly enumerated with their source line and fields.
"""
from __future__ import annotations
from collections import Counter
from .sap2000_geometry import iter_records
from .sap2000_advanced_loads import extract_advanced_loads

def audit_distributed_load_completeness(archive) -> dict:
    parsed = extract_advanced_loads(archive)
    by_line = {x.source_line for x in parsed.distributed}
    rows, counts = [], Counter()
    for record in iter_records(archive):
        if record.table != "FRAME LOADS - DISTRIBUTED":
            continue
        fields = dict(record.fields)
        status = "PARSED" if record.line in by_line else "PRESERVED_ONLY"
        counts[status] += 1
        rows.append({"sourceLine": record.line, "sourceFields": list(record.fields),
                     "rawRecord": record.raw, "status": status,
                     "coreMapped": False})
    if counts["PARSED"] != len(parsed.distributed):
        raise ValueError("SAP_DISTRIBUTED_LOAD_RECONCILIATION_MISMATCH")
    return {"sourceHash": archive.sourceHash, "rawRowCount": len(rows),
            "parsedCount": counts["PARSED"],
            "preservedOnlyCount": counts["PRESERVED_ONLY"],
            "reconciled": len(rows) == sum(counts.values()),
            "records": rows, "coreMappingValidated": False}
