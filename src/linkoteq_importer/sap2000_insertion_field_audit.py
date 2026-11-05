"""Inventory source insertion-point fields without assuming zero offset.

SAP insertion assignment names and units are retained verbatim. This audit
identifies non-empty and nonzero numeric fields but does not infer which fields
are geometric offsets or change load stationing.
"""
from __future__ import annotations
from collections import Counter
from decimal import Decimal, InvalidOperation
from .sap2000_frame_axes import extract_frame_axes

def audit_insertion_source_fields(archive, geometry) -> dict:
    view = extract_frame_axes(archive)
    if view.source_hash != geometry.source_hash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    names, values, numeric_nonzero = Counter(), {}, Counter()
    records = []
    for item in view.insertions:
        nonzero = []
        for key, value in item.fields:
            names[key] += 1
            values.setdefault(key, Counter())[value] += 1
            try:
                number = Decimal(value)
                if number.is_finite() and number != 0:
                    nonzero.append({"field": key, "sourceValue": value})
                    numeric_nonzero[key] += 1
            except InvalidOperation:
                pass
        records.append({"frameId": item.frame_id, "sourceLine": item.source_line,
                        "rawFields": list(item.fields), "nonzeroNumericFields": nonzero,
                        "offsetSemanticsValidated": False})
    return {"sourceHash": archive.sourceHash, "recordCount": len(records),
            "fieldCounts": dict(names),
            "distinctFieldValues": {k: len(v) for k,v in values.items()},
            "sampleFieldValues": {k: sorted(v)[:10] for k,v in values.items()},
            "nonzeroNumericFieldCounts": dict(numeric_nonzero),
            "records": records, "offsetSemanticsValidated": False,
            "zeroOffsetAssumptionAllowed": False, "analysisReady": False}
