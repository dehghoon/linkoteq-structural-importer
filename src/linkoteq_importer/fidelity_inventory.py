"""Conservative, source-referenced fidelity inventory for Import Result v0.1.0.

This is NOT a Core mapping certificate. A source-view parse never counts as
mapped, even when geometry or properties have been interpreted.
"""
from __future__ import annotations

from collections import Counter

def build_fidelity_inventory(result: dict) -> dict:
    if result.get("contract") != "linkoteq.import-result":
        raise ValueError("INVALID_IMPORT_RESULT")
    source = result.get("source", {})
    digest = source.get("sourceHash")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("SOURCE_HASH_MISSING")
    if result.get("coreModel") is not None:
        raise ValueError("CORE_MODEL_REQUIRES_OFFICIAL_VALIDATION")
    views = result.get("sourceViews")
    if not isinstance(views, dict):
        raise ValueError("SOURCE_VIEWS_MISSING")
    records = []
    for kind in sorted(views):
        items = views[kind]
        if not isinstance(items, list):
            raise ValueError("SOURCE_VIEW_NOT_LIST:" + kind)
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError("SOURCE_RECORD_NOT_OBJECT:" + kind)
            record_hash = item.get("sourceHash")
            if record_hash != digest:
                raise ValueError("SOURCE_RECORD_HASH_MISMATCH:" + kind)
            source_id = item.get("sourceId")
            line = item.get("sourceLine")
            if not isinstance(source_id, str) or not source_id:
                raise ValueError("SOURCE_ID_MISSING:" + kind)
            if not isinstance(line, int) or line < 0:
                raise ValueError("SOURCE_LINE_INVALID:" + kind)
            records.append({
                "kind": kind,
                "ordinal": index,
                "sourceId": source_id,
                "sourceLine": line,
                "sourceHash": digest,
                "sourceUnitsDeclaration": result.get("sourceUnitsDeclaration"),
                "status": "preserved-only",
                "reason": "SOURCE_VIEW_NOT_OFFICIALLY_CORE_VALIDATED",
            })
    counts = Counter(record["status"] for record in records)
    return {
        "contract": "linkoteq.import-fidelity-inventory",
        "version": "0.1.0",
        "targetCoreContract": result.get("targetCoreContract"),
        "sourceHash": digest,
        "sourceFormat": result.get("sourceFormat"),
        "sourceArchiveAvailable": source.get("archiveAvailable") is True,
        "canonicalMappingValidated": False,
        "records": records,
        "counts": dict(counts),
        "unparsedSourceCoverage": "unknown-original-bytes-preserved",
        "diagnostics": list(result.get("diagnostics", [])),
    }
