"""Pinned real SAP fixture integration of Core v0.6 conversion gates."""
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_properties import extract_properties
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.partial_structural_model import build_partial_model
from linkoteq_importer.sap2000_v06_gate import build_sap2000_v06_gate_report

def run():
    data = Path("docs/MTDENN~1.$2k").read_bytes()
    digest = "8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    assert sha256(data).hexdigest() == digest
    limits = Limits(20_000_000, 200_000, 200_000, 2_000_000,
                    200_000, 300_000, 300_000, 100_000_000)
    archive = archive_bytes(data, filename="MTDENN~1.$2k", extension=".$2k",
                            project_ref="ci-fixture", namespace="ci",
                            policy_id="read-only", limits=limits)
    geometry = extract_geometry(archive)
    properties = extract_properties(archive)
    boundaries = extract_boundaries(archive)
    partial = build_partial_model(geometry, properties, stress_unit="kPa",
                                  density_unit="kg/m3", length_unit="m")
    report = build_sap2000_v06_gate_report(partial, geometry, boundaries,
                                           project_id="real-sap-fixture")
    assert report["sourceHash"] == digest
    assert report["targetSchemaVersion"] == "0.6"
    assert report["status"] == "blocked"
    assert report["coreModel"] is None
    assert not report["canonicalMappingValidated"] and not report["analysisReady"]
    assert report["counts"]["sourceNodes"] == 388
    assert report["counts"]["sourceMembers"] == 609
    assert report["counts"]["mappedSupports"] == 55
    assert report["counts"]["mappedBinaryFrameReleases"] == 180
    assert report["blockers"]["total"] >= 64
    assert archive.retrieve() == data
    print("PASS SAP2000 Core v0.6 combined gate", report["counts"],
          "blockerTypes", report["blockers"]["byCode"])

if __name__ == "__main__":
    run()
