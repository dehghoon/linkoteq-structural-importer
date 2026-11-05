"""Conservative display-only projection of GLOBAL Cartesian SAP grid lines.

Does not claim a validated Core grid schema. Unknown variants remain in
sourceGridAudit, never silently interpreted as straight lines.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from .sap2000_geometry import iter_records, _unique

def project_source_grid_preview(archive) -> dict:
    lines, deferred = [], []
    for record in iter_records(archive):
        if record.table != "GRID LINES":
            continue
        f = _unique(record)
        axis = f.get("axisdir", "").upper()
        system = f.get("coordsys", "")
        identifier = f.get("gridid")
        raw_position = f.get("xryzcoord")
        try:
            position = Decimal(raw_position) if raw_position is not None else None
            if position is not None and not position.is_finite():
                position = None
        except InvalidOperation:
            position = None
        if system.upper() != "GLOBAL" or axis not in ("X", "Y", "Z") or not identifier or position is None:
            deferred.append({"sourceLine": record.line, "sourceFields": list(record.fields),
                             "rawRecord": record.raw, "reason": "GRID_COORDINATE_SEMANTICS_UNSUPPORTED"})
            continue
        lines.append({"id": identifier, "axis": axis, "coordinate": str(position),
                      "coordinateSystem": system, "sourceLine": record.line,
                      "sourceFields": list(record.fields), "displayOnly": True})
    return {"sourceHash": archive.sourceHash, "gridLines": lines,
            "deferredGridLines": deferred, "coreGridMappingValidated": False,
            "analysisReady": False}
