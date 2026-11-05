"""Project a fully resolved SAP geometry/property subset to Core v0.6 shape.

This is a *candidate*, not a certified canonical model: loads, diaphragms,
releases and offsets are deliberately NOT represented here. Consumers must
check the explicit omissions and never use it for analysis.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation

_REQUIRED_MATERIAL = ("E", "G", "nu", "rho")
_REQUIRED_SECTION = ("A", "Iy", "Iz", "J")

def _number(value, label):
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError("INVALID_NUMBER:" + label)
    if not d.is_finite():
        raise ValueError("NONFINITE_NUMBER:" + label)
    return float(d)

def _unit(value, unit, label):
    return {"value": _number(value, label), "unit": unit}

def project_geometry_properties_v06(partial: dict, *, project_id: str) -> dict:
    if partial.get("kind") != "partial-structural-model-not-analysis-ready":
        raise ValueError("UNEXPECTED_PARTIAL_MODEL")
    if partial.get("analysisReady") is not False or partial.get("mapped_to_core") is not False:
        raise ValueError("UNSAFE_SOURCE_MODEL_STATUS")
    if not project_id:
        raise ValueError("PROJECT_ID_REQUIRED")
    problems = list(partial.get("unresolvedReferences", []))
    problems += list(partial.get("unmappedProperties", []))
    problems += list(partial.get("diagnostics", []))
    for m in partial["members"]:
        problems += m.get("diagnostics", [])
    if problems:
        return {"status": "blocked", "candidate": None, "diagnostics": sorted(set(problems)),
                "targetSchemaVersion": "0.6"}
    material_map = {m["sourceId"]: m for m in partial["materialProperties"]}
    section_map = {s["sourceId"]: s for s in partial["sectionProperties"]}
    members = []
    for member in partial["members"]:
        sid = member.get("sectionId", "").removeprefix("sap2000:section:")
        mid = member.get("materialId", "").removeprefix("sap2000:material:")
        if sid not in section_map or mid not in material_map:
            return {"status": "blocked", "candidate": None,
                    "diagnostics": ["UNRESOLVED_MEMBER_PROPERTIES:" + member["sourceId"]],
                    "targetSchemaVersion": "0.6"}
        members.append({"id": member["id"], "type": "other",
                        "startNodeId": member["startNodeId"],
                        "endNodeId": member["endNodeId"],
                        "sectionId": member["sectionId"],
                        "materialId": member["materialId"],
                        "metadata": {"sourceId": member["sourceId"]}})
    nodes = [{"id": n["id"],
              "position": {axis: _number(n[axis], axis) for axis in ("x", "y", "z")}}
             for n in partial["nodes"]]
    materials = []
    for source_id, m in sorted(material_map.items()):
        materials.append({"id": "sap2000:material:" + source_id, "type": "other",
                          "name": source_id, "analysis": {
                              "E": _unit(m["E"], "Pa", "E"),
                              "G": _unit(m["G"], "Pa", "G"),
                              "nu": _number(m["nu"], "nu"),
                              "rho": _unit(m["rho"], "kg/m3", "rho")}})
    sections = []
    for source_id, s in sorted(section_map.items()):
        sections.append({"id": "sap2000:section:" + source_id,
                         "family": "other", "designation": source_id,
                         "analysis": {key: _unit(s[key], "m2" if key == "A" else "m4", key)
                                      for key in _REQUIRED_SECTION}})
    candidate = {
        "schemaVersion": "0.6",
        "project": {"id": project_id, "name": project_id, "units": "SI"},
        "levels": [], "grids": [], "nodes": nodes, "members": members,
        "surfaces": [], "diaphragms": [], "materials": materials,
        "sections": sections, "supports": [], "loadCases": [],
        "loads": [], "loadCombinations": []
    }
    return {
        "status": "candidate-unvalidated", "targetSchemaVersion": "0.6",
        "candidate": candidate, "canonicalMappingValidated": False,
        "analysisReady": False, "sourceHash": partial["sourceHash"],
        "omittedDomains": ["member-type-classification", "local-axes",
                           "end-releases", "insertion-offsets", "diaphragms",
                           "supports", "springs", "nodal-loads", "member-loads",
                           "surface-loads", "self-weight", "load-combinations",
                           "analysis-requests", "source-vendor-extensions"],
        "diagnostics": ["GEOMETRY_PROPERTY_SUBSET_ONLY_NOT_ANALYSIS_READY"]
    }
