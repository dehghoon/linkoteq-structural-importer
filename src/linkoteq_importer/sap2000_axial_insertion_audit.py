"""Audit axial versus transverse SAP frame joint insertion offsets.

JtOffsetXI/XJ are recorded as source local-X components, not interpreted
as member-end shortening. Lateral Y/Z components are preserved and flagged.
No load stations are changed without verified SAP insertion semantics.
"""
from __future__ import annotations
from collections import Counter
from decimal import Decimal, InvalidOperation
from .sap2000_frame_axes import extract_frame_axes
from .sap2000_advanced_loads import extract_advanced_loads

_KEYS = ("JtOffsetXI", "JtOffsetXJ", "JtOffsetYI", "JtOffsetYJ",
         "JtOffsetZI", "JtOffsetZJ")

def audit_axial_insertion_offsets(archive, geometry) -> dict:
    axes = extract_frame_axes(archive)
    loads = extract_advanced_loads(archive)
    if axes.source_hash != geometry.source_hash or loads.source_hash != geometry.source_hash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    loaded = Counter(x.frame_id for x in loads.distributed)
    results = []
    summary = Counter()
    for item in axes.insertions:
        f = dict(item.fields)
        present = {k: f[k] for k in _KEYS if k in f}
        invalid = []
        nonzero = []
        for k, raw in present.items():
            try:
                v = Decimal(raw)
                if not v.is_finite():
                    invalid.append(k)
                elif v != 0:
                    nonzero.append(k)
            except InvalidOperation:
                invalid.append(k)
        axial = [k for k in nonzero if k in ("JtOffsetXI", "JtOffsetXJ")]
        transverse = [k for k in nonzero if k not in ("JtOffsetXI", "JtOffsetXJ")]
        count = loaded[item.frame_id]
        if count:
            summary["loadedFrames"] += 1
            summary["loadedRecords"] += count
            if axial:
                summary["loadsWithNonzeroAxialOffset"] += count
            if transverse:
                summary["loadsWithNonzeroTransverseOffset"] += count
            if invalid:
                summary["loadsWithInvalidOffset"] += count
            if not present:
                summary["loadsWithoutExplicitOffsetFields"] += count
        results.append({"frameId": item.frame_id, "sourceLine": item.source_line,
                        "loadedRecordCount": count, "sourceOffsetFields": present,
                        "nonzeroAxialFields": axial,
                        "nonzeroTransverseFields": transverse,
                        "invalidNumericFields": invalid,
                        "stationCorrectionApplied": False})
    return {"sourceHash": archive.sourceHash, "assignmentCount": len(results),
            "summary": dict(summary), "assignments": results,
            "axialOffsetStationSemanticsVerified": False,
            "transverseOffsetForceMomentEffectsVerified": False,
            "coreStationMappingValidated": False, "analysisReady": False}
