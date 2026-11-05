"""Classify SAP2000 distributed-load rows not handled by current parser.

Never infer force semantics from an unknown magnitude or distance field.
Preserve exact raw row and source line while exposing a concise reason.
"""
from __future__ import annotations
from collections import Counter
from .sap2000_geometry import iter_records, _unique
from .sap2000_advanced_loads import extract_advanced_loads

def diagnose_unparsed_distributed_loads(archive) -> dict:
    parsed = {x.source_line for x in extract_advanced_loads(archive).distributed}
    reasons = Counter()
    examples = {}
    rows = []
    for record in iter_records(archive):
        if record.table != "FRAME LOADS - DISTRIBUTED" or record.line in parsed:
            continue
        f = _unique(record)
        distance = f.get("disttype", "")
        if distance.casefold() not in ("reldist", "absdist"):
            reason = "UNSUPPORTED_DISTANCE_TYPE"
        elif "foverla" not in f or "foverlb" not in f:
            reason = "UNSUPPORTED_MAGNITUDE_FIELDS"
        else:
            reason = "UNKNOWN_PARSER_GAP"
        reasons[reason] += 1
        examples.setdefault(reason, [])
        if len(examples[reason]) < 5:
            examples[reason].append({"line": record.line, "fields": list(record.fields)})
        rows.append({"sourceLine": record.line, "frameId": f.get("frame"),
                     "patternId": f.get("loadpat"), "reason": reason,
                     "sourceFields": list(record.fields), "rawRecord": record.raw,
                     "mappedToCore": False})
    return {"sourceHash": archive.sourceHash, "preservedOnlyCount": len(rows),
            "reasonCounts": dict(reasons), "examples": examples,
            "records": rows, "coreMappingValidated": False}
