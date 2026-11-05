"""Real SAP2000 fixture gate for Core v0.6 candidate projection.

The pinned engineering file may contain unresolved properties. Such a file
must be blocked, not silently repaired or converted into an analysis model.
"""
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_properties import extract_properties
from linkoteq_importer.partial_structural_model import build_partial_model
from linkoteq_importer.core_v06_candidate import project_geometry_properties_v06

EXPECTED = "8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"

def run():
    data = Path("docs/MTDENN~1.$2k").read_bytes()
    assert sha256(data).hexdigest() == EXPECTED
    limits = Limits(20_000_000, 200_000, 200_000, 2_000_000,
                    200_000, 300_000, 300_000, 100_000_000)
    archive = archive_bytes(data, filename="MTDENN~1.$2k", extension=".$2k",
                            project_ref="ci-fixture", namespace="ci",
                            policy_id="read-only", limits=limits)
    geometry = extract_geometry(archive)
    properties = extract_properties(archive)
    assert len(geometry.joints) == 388
    assert len(geometry.frames) == 609
    assert len(properties.sections) == 84
    assert geometry.declared_units == "KN, m, C"
    partial = build_partial_model(geometry, properties, stress_unit="kPa",
                                  density_unit="kg/m3", length_unit="m")
    assert len(partial["nodes"]) == 388
    assert len(partial["members"]) == 609
    assert partial["sourceHash"] == EXPECTED
    result = project_geometry_properties_v06(partial, project_id="real-sap-fixture")
    assert result["targetSchemaVersion"] == "0.6"
    if result["status"] == "blocked":
        assert result["candidate"] is None
        assert result["diagnostics"]
        print("PASS real SAP fixture blocked on unresolved engineering data:",
              len(result["diagnostics"]), "diagnostics")
    else:
        assert result["status"] == "candidate-unvalidated"
        assert not result["analysisReady"]
        assert not result["canonicalMappingValidated"]
        candidate = result["candidate"]
        assert len(candidate["nodes"]) == 388
        assert len(candidate["members"]) == 609
        print("PASS real SAP fixture produced unvalidated Core v0.6 candidate")
    assert archive.retrieve() == data

if __name__ == "__main__":
    run()
