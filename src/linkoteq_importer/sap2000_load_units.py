"""Conservative SAP2000 load unit preflight; never infer source force units.

A declaration is evidence, not authorization for numeric conversion. The
source force/length basis and dimensional load conventions must be verified
against the official Core contract before mapping.
"""
from __future__ import annotations
from .sap2000_geometry import iter_records, _unique

def audit_sap2000_load_units(archive, geometry) -> dict:
    declarations = []
    for record in iter_records(archive):
        if record.table != "PROGRAM CONTROL":
            continue
        fields = _unique(record)
        if "currunits" in fields:
            declarations.append({"sourceLine": record.line,
                                 "rawUnitDeclaration": fields["currunits"]})
    distinct = sorted({item["rawUnitDeclaration"] for item in declarations})
    issues = []
    if not declarations:
        issues.append("SOURCE_UNITS_NOT_DECLARED")
    if len(distinct) > 1:
        issues.append("MULTIPLE_SOURCE_UNIT_DECLARATIONS_REQUIRE_REVIEW")
    if geometry.declared_units and geometry.declared_units not in distinct:
        issues.append("GEOMETRY_UNIT_DECLARATION_MISMATCH")
    return {
        "sourceHash": archive.sourceHash,
        "declarations": declarations,
        "distinctDeclarations": distinct,
        "issues": issues,
        "numericLoadConversionPerformed": False,
        "forceDimensionValidated": False,
        "momentDimensionValidated": False,
        "distributedLoadDimensionValidated": False,
        "analysisReady": False,
    }
