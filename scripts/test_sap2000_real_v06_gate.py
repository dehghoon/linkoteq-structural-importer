"""Pinned real SAP fixture integration of Core v0.6 conversion gates."""
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_properties import extract_properties
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.partial_structural_model import build_partial_model
from linkoteq_importer.sap2000_v06_gate import build_sap2000_v06_gate_report
from linkoteq_importer.sap2000_material_audit import audit_material_origins
from linkoteq_importer.sap2000_tapered_audit import audit_tapered_source
from linkoteq_importer.sap2000_nonprismatic import extract_nonprismatic_segments
from linkoteq_importer.sap2000_nonprismatic_references import audit_nonprismatic_end_sections
from linkoteq_importer.sap2000_nonprismatic_materials import resolve_nonprismatic_member_materials

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
    audit = audit_material_origins(properties, partial["unresolvedReferences"])
    assert audit["totalUnresolvedFrames"] == 54
    assert sum(item["frameCount"] for item in audit["bySourceSection"]) == 54
    assert all(item["resolution"] == "not-mapped-no-substitution" for item in audit["records"])
    print("SAP_MATERIAL_ORIGIN_AUDIT", audit["bySourceSection"])
    tapered = audit_tapered_source(archive)
    assert tapered["sourceHash"] == digest
    assert tapered["recordCount"] > 0
    assert not tapered["mappedToCore"] and not tapered["analysisReady"]
    print("SAP_TAPERED_SOURCE_TABLES", tapered["candidateTables"])
    print("SAP_TAPERED_SOURCE_RECORDS", tapered["records"][:15])
    print("SAP_NONPRISMATIC_SOURCE_RECORDS", [r for r in tapered["records"] if "NONPRISMATIC" in r["table"]][:20])
    nonprismatic = extract_nonprismatic_segments(archive)
    assert nonprismatic["segmentCount"] > 0
    assert nonprismatic["mappingStatus"] == "preserved-extension"
    assert not nonprismatic["mappedToCore"]
    assert all(segment["fields"] for segment in nonprismatic["segments"])
    print("SAP_NONPRISMATIC_PRESERVED_SEGMENTS", nonprismatic["segmentCount"])
    references = audit_nonprismatic_end_sections(archive, properties)
    assert len(references["segments"]) == 1
    segment = references["segments"][0]
    assert segment["nonprismaticSectionId"] == "Tapered Beam"
    assert [e["sectionId"] for e in segment["endpoints"]] == ["89 W Beam", "W410X149"]
    assert segment["ei33Variation"] == "Cubic"
    assert segment["ei22Variation"] == "Linear"
    assert not references["coreAnalyticalSectionMapped"]
    print("SAP_NONPRISMATIC_ENDPOINT_REFERENCES", segment["endpoints"])
    print("SAP_NONPRISMATIC_ENDPOINT_DIAGNOSTICS", references["diagnosticCounts"])
    material_resolution = resolve_nonprismatic_member_materials(archive, properties, partial)
    assert len(material_resolution["resolutions"]) == 54
    assert material_resolution["unresolved"] == []
    assert all(item["resolvedMaterialId"] == "A992Fy50" for item in material_resolution["resolutions"])
    assert all(not item["analyticalSectionMapped"] for item in material_resolution["resolutions"])
    print("SAP_NONPRISMATIC_MATERIAL_RESOLVED", len(material_resolution["resolutions"]))
    assert archive.retrieve() == data
    print("PASS SAP2000 Core v0.6 combined gate", report["counts"],
          "blockerTypes", report["blockers"]["byCode"])

if __name__ == "__main__":
    run()
