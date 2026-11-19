"""Validate SAP2000 combination dependency graphs without evaluating factors.

Linear-add status alone never authorizes Core mapping; cycles and missing
references are explicitly reported, including source line provenance.
"""
from __future__ import annotations
from .sap2000_advanced_loads import extract_advanced_loads

def audit_combination_graph(archive) -> dict:
    view = extract_advanced_loads(archive)
    cases = {case.source_id for case in view.cases}
    combos = {combo.source_id: combo for combo in view.combinations}
    edges = {name: [] for name in combos}
    issues = []
    for combo in view.combinations:
        for term in combo.terms:
            target = term.case_or_combo_id
            if target in combos:
                edges[combo.source_id].append(target)
            elif target not in cases:
                issues.append({"code": "UNKNOWN_COMBINATION_REFERENCE",
                               "combinationId": combo.source_id, "targetId": target,
                               "sourceLine": term.source_line})
    visited, active = set(), set()
    def visit(name, path):
        if name in active:
            issues.append({"code": "COMBINATION_CYCLE",
                           "path": path + [name]})
            return
        if name in visited:
            return
        active.add(name)
        for target in edges[name]:
            visit(target, path + [name])
        active.remove(name)
        visited.add(name)
    for name in combos:
        visit(name, [])
    return {
        "sourceHash": archive.sourceHash,
        "combinationCount": len(combos),
        "caseCount": len(cases),
        "dependencyEdges": sum(map(len, edges.values())),
        "issues": issues,
        "sourceParserDiagnostics": list(view.diagnostics),
        "coreLinearMappingValidated": False,
        "analysisReady": False,
    }
