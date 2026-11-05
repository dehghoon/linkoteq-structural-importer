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
from linkoteq_importer.sap2000_v06_material_reconciliation import reconcile_tapered_material_diagnostics
from linkoteq_importer.sap2000_none_sections import audit_none_section_assignments
from linkoteq_importer.sap2000_v06_fidelity import build_sap2000_v06_fidelity_supplement

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
                                           project_id="real-sap-fixture", archive=archive, properties=properties)
    assert report["sourceHash"] == digest
    assert report["importFidelity"]["sourceHash"] == digest
    assert report["importFidelity"]["materialIdentityResolution"]["resolvedMaterialCount"] == 54
    assert report["importFidelity"]["explicitNoneSectionAssignments"]["count"] == 4
    assert report["importFidelity"]["coreModel"] is None
    assert "sourceLoads" in report["importFidelity"]
    levels = report["importFidelity"]["sourceLevelAudit"]
    assert not levels["coreLevelMappingValidated"]
    print("SAP_V06_SOURCE_LEVEL_TABLES", levels["levelTableCounts"], levels["sourceRecordCount"], levels["sourceRecords"][:3])
    grids = report["importFidelity"]["sourceGridAudit"]
    assert not grids["coreGridMappingValidated"]
    print("SAP_V06_SOURCE_GRID_TABLES", grids["gridTableCounts"], grids["sourceRecordCount"], grids["sourceRecords"][:3])
    unparsed = report["importFidelity"]["unparsedDistributedLoadDiagnostics"]
    assert unparsed["preservedOnlyCount"] == 0
    print("SAP_V06_UNPARSED_LOAD_REASONS", unparsed["reasonCounts"], unparsed["examples"])
    completeness = report["importFidelity"]["distributedLoadSourceCompleteness"]
    assert completeness["reconciled"]
    print("SAP_V06_RAW_DISTRIBUTED_ROWS", completeness["rawRowCount"], completeness["parsedCount"], completeness["preservedOnlyCount"])
    assert completeness["rawRowCount"] == completeness["parsedCount"] + completeness["preservedOnlyCount"]
    assert completeness["parsedCount"] == 1810
    assert completeness["preservedOnlyCount"] == 0
    print("SAP_V06_DISTRIBUTED_LOAD_COMPLETENESS", completeness["rawRowCount"], completeness["parsedCount"], completeness["preservedOnlyCount"])
    station_ready = report["importFidelity"]["distributedStationReadiness"]
    assert station_ready["recordCount"] == 1810
    assert station_ready["coreReadyCount"] == 0
    assert station_ready["reasonCounts"]["TRANSVERSE_OFFSET_FORCE_MOMENT_EFFECT_UNVERIFIED"] >= 672
    assert station_ready["reasonCounts"]["EXPLICIT_OFFSET_FIELDS_ABSENT"] >= 942
    print("SAP_V06_STATION_READINESS", station_ready["reasonCounts"])
    axial = report["importFidelity"]["axialInsertionOffsetAudit"]
    assert axial["assignmentCount"] == 609
    assert axial["summary"]["loadedRecords"] == 1810
    assert not axial["axialOffsetStationSemanticsVerified"]
    print("SAP_V06_AXIAL_INSERTION_OFFSETS", axial["summary"])
    insertion_fields = report["importFidelity"]["insertionSourceFieldAudit"]
    assert insertion_fields["recordCount"] == 609
    assert not insertion_fields["zeroOffsetAssumptionAllowed"]
    print("SAP_V06_INSERTION_FIELDS", insertion_fields["fieldCounts"], insertion_fields["nonzeroNumericFieldCounts"], insertion_fields["sampleFieldValues"])
    insertion_audit = report["importFidelity"]["loadStationInsertionAudit"]
    assert insertion_audit["insertionAssignmentCount"] == 609
    assert not insertion_audit["insertionOffsetsInterpreted"]
    assert not insertion_audit["coreStationMappingValidated"]
    print("SAP_V06_LOAD_INSERTION_INTERACTIONS", insertion_audit["loadedFramesWithInsertionAssignment"], insertion_audit["affectedLoadCount"])
    stations = report["importFidelity"]["distributedLoadStationAudit"]
    assert stations["recordCount"] + stations["unresolvedCount"] == 1810
    assert not stations["offsetAware"]
    print("SAP_V06_LOAD_STATIONS", stations["recordCount"], stations["unresolvedCount"], stations["issues"][:3])
    vectors = report["importFidelity"]["globalDistributedVectorCandidates"]
    assert len(vectors["vectorCandidates"]) == 528
    assert len(vectors["deferredLoads"]) == 1282
    assert all(x["sourceDirection"].upper() in ("Y", "Z") for x in vectors["vectorCandidates"])
    assert len([x for x in vectors["deferredLoads"] if x["reason"] == "DIRECTION_OR_LOAD_TYPE_REQUIRES_SEMANTIC_VERIFICATION"]) == 1282
    print("SAP_V06_DEFERRED_DIRECTIONS", sorted({x["direction"] for x in vectors["deferredLoads"]}))
    assert not vectors["gravitySignVerified"] and not vectors["mappedToCore"]
    print("SAP_V06_GLOBAL_LOAD_VECTORS", len(vectors["vectorCandidates"]), len(vectors["deferredLoads"]))
    direction_audit = report["importFidelity"]["distributedLoadDirectionAudit"]
    assert direction_audit["recordCount"] == 1810
    assert not direction_audit["globalVectorMappingValidated"]
    print("SAP_V06_DISTRIBUTED_DIRECTIONS", direction_audit["byCoordinateSystem"], direction_audit["byDirection"], direction_audit["issueCounts"])
    si_loads = report["importFidelity"]["loadSIMagnitudeCandidates"]
    assert si_loads["sourceUnits"] == "KN, m, C"
    assert len(si_loads["nodalLoadsSI"]) == 2
    assert len(si_loads["distributedMagnitudeCandidatesSI"]) == 1810
    assert sum(x["sourceLoadType"].casefold() == "moment" for x in si_loads["distributedMagnitudeCandidatesSI"]) == 196
    assert all(x["magnitudeUnit"] == "N*m/m" and x["siMagnitudeCandidates"] is not None
               for x in si_loads["distributedMagnitudeCandidatesSI"] if x["sourceLoadType"].casefold() == "moment")
    assert not si_loads["coreMappingValidated"]
    assert not si_loads["localDirectionTransformsValidated"]
    assert all(x["siMagnitudeCandidates"] is None or x["magnitudeUnit"] in ("N/m", "N*m/m")
               for x in si_loads["distributedMagnitudeCandidatesSI"])
    print("SAP_V06_SI_LOAD_MAGNITUDES", len(si_loads["nodalLoadsSI"]), len(si_loads["distributedMagnitudeCandidatesSI"]))
    load_units = report["importFidelity"]["loadUnitAudit"]
    assert load_units["sourceHash"] == digest
    assert not load_units["numericLoadConversionPerformed"]
    assert not load_units["analysisReady"]
    print("SAP_V06_LOAD_UNITS", load_units["distinctDeclarations"], load_units["issues"])
    combination_graph = report["importFidelity"]["combinationGraphAudit"]
    assert combination_graph["combinationCount"] == 48
    assert combination_graph["caseCount"] == 11
    assert not combination_graph["coreLinearMappingValidated"]
    print("SAP_V06_COMBINATION_GRAPH", {"edges": combination_graph["dependencyEdges"], "issues": combination_graph["issues"][:10]})
    load_reference_audit = report["importFidelity"]["loadReferenceAudit"]
    assert load_reference_audit["counts"]["distributedFrameLoads"] == 1810
    assert not load_reference_audit["unitsVerified"]
    assert not load_reference_audit["analysisReady"]
    print("SAP_V06_LOAD_REFERENCE_AUDIT", load_reference_audit["byCode"])
    source_loads = report["importFidelity"]["sourceLoads"]
    assert len(source_loads["distributedFrameLoads"]) == 1810
    assert len(source_loads["loadCases"]) == 11
    assert len(source_loads["loadCombinations"]) == 48
    assert not source_loads["mappedToCore"]
    print("SAP_V06_LOAD_FIDELITY", {key: len(source_loads[key]) for key in ("patterns", "jointForces", "distributedFrameLoads", "loadCases", "loadCombinations")})
    assert "frameLocalAxes" in report["importFidelity"]
    assert "diaphragmConstraints" in report["importFidelity"]
    assert not report["importFidelity"]["frameLocalAxes"]["mappedToCore"]
    assert not report["importFidelity"]["diaphragmConstraints"]["mappedToCore"]
    print("SAP_V06_AXES_DIAPHRAGMS", {
        "axisRotations": len(report["importFidelity"]["frameLocalAxes"]["rotations"]),
        "insertions": len(report["importFidelity"]["frameLocalAxes"]["insertions"]),
        "diaphragmDefinitions": len(report["importFidelity"]["diaphragmConstraints"]["definitions"]),
        "diaphragmMemberships": len(report["importFidelity"]["diaphragmConstraints"]["memberships"]),
    })
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
    reconciliation = reconcile_tapered_material_diagnostics(archive, properties, partial)
    assert reconciliation["resolvedMaterialCount"] == 54
    assert reconciliation["originalUnresolvedCount"] == 58
    assert reconciliation["remainingReferenceCount"] == 4
    assert all(item.startswith("UNKNOWN_SECTION:") for item in reconciliation["outstandingUnresolvedReferences"])
    assert not reconciliation["analysisReady"] and not reconciliation["canonicalCoreValidated"]
    print("SAP_V06_MATERIAL_RECONCILIATION", {k: reconciliation[k] for k in ("originalUnresolvedCount", "resolvedMaterialCount", "remainingReferenceCount", "nonprismaticSectionStatus")})
    none_sections = audit_none_section_assignments(properties, geometry)
    assert none_sections["count"] == 4
    assert all(item["frameExists"] for item in none_sections["records"])
    assert all(item["sourceSectionValue"] == "None" for item in none_sections["records"])
    assert not none_sections["analysisReady"]
    print("SAP_EXPLICIT_NONE_SECTIONS", none_sections["records"])
    fidelity = build_sap2000_v06_fidelity_supplement(archive, geometry, properties, partial)
    assert fidelity["targetCoreContract"] == "v0.6.0"
    assert fidelity["originalSourcePreserved"]
    assert fidelity["materialIdentityResolution"]["resolvedMaterialCount"] == 54
    assert fidelity["explicitNoneSectionAssignments"]["count"] == 4
    assert len(fidelity["nonprismaticSectionDefinitions"]["segments"]) == 1
    assert fidelity["coreModel"] is None and not fidelity["analysisReady"]
    print("SAP_V06_FIDELITY_SUPPLEMENT", fidelity["engineeringDisposition"])
    assert archive.retrieve() == data
    print("PASS SAP2000 Core v0.6 combined gate", report["counts"],
          "blockerTypes", report["blockers"]["byCode"])

if __name__ == "__main__":
    run()
