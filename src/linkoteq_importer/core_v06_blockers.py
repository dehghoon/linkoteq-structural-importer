"""Deterministic diagnostic classification for SAP2000 Core v0.6 blockers.

No silent substitutions. Group repeated diagnostics by code while preserving
the original complete list for source investigation.
"""
from __future__ import annotations
from collections import Counter

def classify_blockers(diagnostics: list[str]) -> dict:
    groups: dict[str, list[str]] = {}
    for entry in diagnostics:
        if not isinstance(entry, str) or not entry:
            raise ValueError("INVALID_DIAGNOSTIC")
        code = entry.split(":", 1)[0]
        groups.setdefault(code, []).append(entry)
    return {
        "total": len(diagnostics),
        "unique": len(set(diagnostics)),
        "byCode": {code: {"count": len(items), "examples": items[:5]}
                   for code, items in sorted(groups.items())},
        "allDiagnostics": list(diagnostics),
        "unresolved": bool(diagnostics),
        "policy": "no-silent-substitution",
    }
