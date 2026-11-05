"""Executable synthetic gate for Core v0.6 geometry/property candidate."""
from linkoteq_importer.core_v06_candidate import project_geometry_properties_v06

def run():
    p = {
        "kind": "partial-structural-model-not-analysis-ready",
        "analysisReady": False, "mapped_to_core": False,
        "sourceHash": "source-test", "unresolvedReferences": [],
        "unmappedProperties": [], "diagnostics": [],
        "nodes": [{"id": "sap2000:node:1", "x": "0", "y": "0", "z": "0"},
                  {"id": "sap2000:node:2", "x": "1.5", "y": "0", "z": "0"}],
        "members": [{"id": "sap2000:member:1", "sourceId": "1",
                     "startNodeId": "sap2000:node:1",
                     "endNodeId": "sap2000:node:2",
                     "sectionId": "sap2000:section:W",
                     "materialId": "sap2000:material:S",
                     "diagnostics": []}],
        "materialProperties": [{"sourceId": "S", "E": "200000000000",
                                "G": "80000000000", "nu": "0.3", "rho": "7850"}],
        "sectionProperties": [{"sourceId": "W", "A": "0.01",
                               "Iy": "0.00001", "Iz": "0.00002", "J": "0.000001"}],
    }
    result = project_geometry_properties_v06(p, project_id="sample")
    assert result["status"] == "candidate-unvalidated"
    assert not result["analysisReady"] and not result["canonicalMappingValidated"]
    model = result["candidate"]
    assert model["schemaVersion"] == "0.6"
    assert model["members"][0]["startNodeId"] == "sap2000:node:1"
    assert model["members"][0]["sectionId"] == model["sections"][0]["id"]
    assert model["members"][0]["materialId"] == model["materials"][0]["id"]
    assert model["sections"][0]["analysis"]["A"] == {"value": 0.01, "unit": "m2"}
    assert model["materials"][0]["analysis"]["E"] == {"value": 200000000000.0, "unit": "Pa"}
    assert "end-releases" in result["omittedDomains"]
    p["unresolvedReferences"] = ["UNKNOWN_SECTION:1:Missing"]
    blocked = project_geometry_properties_v06(p, project_id="sample")
    assert blocked["status"] == "blocked" and blocked["candidate"] is None
    print("PASS Core v0.6 candidate projection and fail-closed unresolved references")

if __name__ == "__main__":
    run()
