"""Import Fidelity supplement for SAP2000 Core v0.6 nonprismatic work.

All source diagnostics remain inspectable. Material identity resolution and
explicit None sections do not authorize an analytical Core model.
"""
from __future__ import annotations
from .sap2000_v06_material_reconciliation import reconcile_tapered_material_diagnostics
from .sap2000_none_sections import audit_none_section_assignments
from .sap2000_nonprismatic_references import audit_nonprismatic_end_sections
from .sap2000_frame_axes import extract_frame_axes
from .sap2000_diaphragms import extract_diaphragms
from .sap2000_loads import extract_loads
from .sap2000_advanced_loads import extract_advanced_loads
from .sap2000_load_reference_audit import audit_sap2000_load_references
from .sap2000_combination_graph import audit_combination_graph
from .sap2000_load_units import audit_sap2000_load_units
from .sap2000_load_si import convert_sap2000_kn_m_load_magnitudes
from .sap2000_load_direction_audit import audit_distributed_load_semantics
from .sap2000_global_load_vectors import project_global_distributed_vectors
from .sap2000_load_stations import audit_distributed_load_stations
from .sap2000_load_insertion_audit import audit_load_station_insertion_interactions
from .sap2000_insertion_field_audit import audit_insertion_source_fields
from .sap2000_axial_insertion_audit import audit_axial_insertion_offsets
from .sap2000_station_readiness import classify_distributed_station_readiness
from .sap2000_load_completeness import audit_distributed_load_completeness
from .sap2000_unparsed_load_diagnostics import diagnose_unparsed_distributed_loads
from .sap2000_grid_audit import audit_source_grids

def build_sap2000_v06_fidelity_supplement(archive, geometry, properties,
                                           partial: dict) -> dict:
    hashes = {archive.sourceHash, geometry.source_hash,
              properties.source_hash, partial.get("sourceHash")}
    if len(hashes) != 1:
        raise ValueError("SOURCE_HASH_MISMATCH")
    materials = reconcile_tapered_material_diagnostics(archive, properties, partial)
    none_sections = audit_none_section_assignments(properties, geometry)
    tapered = audit_nonprismatic_end_sections(archive, properties)
    axes = extract_frame_axes(archive)
    diaphragms = extract_diaphragms(archive)
    loads = extract_loads(archive)
    advanced_loads = extract_advanced_loads(archive)
    load_audit = audit_sap2000_load_references(archive, geometry)
    combination_graph = audit_combination_graph(archive)
    load_stations = audit_distributed_load_stations(archive, geometry)
    insertion_interactions = audit_load_station_insertion_interactions(archive, geometry)
    insertion_fields = audit_insertion_source_fields(archive, geometry)
    axial_offsets = audit_axial_insertion_offsets(archive, geometry)
    station_readiness = classify_distributed_station_readiness(archive, geometry)
    load_completeness = audit_distributed_load_completeness(archive)
    unparsed_loads = diagnose_unparsed_distributed_loads(archive)
    source_grids = audit_source_grids(archive)
    load_directions = audit_distributed_load_semantics(archive, geometry)
    global_vectors = None
    load_units = audit_sap2000_load_units(archive, geometry)
    if load_units["distinctDeclarations"] == ["KN, m, C"] and not load_units["issues"]:
        global_vectors = project_global_distributed_vectors(archive, geometry)
    load_si = (convert_sap2000_kn_m_load_magnitudes(archive, geometry)
               if load_units["distinctDeclarations"] == ["KN, m, C"] and not load_units["issues"]
               else None)
    if any(h != archive.sourceHash for h in (axes.source_hash, diaphragms.source_hash,
                                              loads.source_hash, advanced_loads.source_hash)):
        raise ValueError("SOURCE_HASH_MISMATCH")
    return {
        "targetCoreContract": "v0.6.0",
        "sourceHash": archive.sourceHash,
        "originalSourcePreserved": True,
        "originalDiagnostics": list(partial["unresolvedReferences"]),
        "materialIdentityResolution": materials,
        "explicitNoneSectionAssignments": none_sections,
        "nonprismaticSectionDefinitions": tapered,
        "loadReferenceAudit": load_audit,
        "combinationGraphAudit": combination_graph,
        "loadUnitAudit": load_units,
        "distributedLoadDirectionAudit": load_directions,
        "distributedLoadStationAudit": load_stations,
        "loadStationInsertionAudit": insertion_interactions,
        "insertionSourceFieldAudit": insertion_fields,
        "axialInsertionOffsetAudit": axial_offsets,
        "distributedStationReadiness": station_readiness,
        "distributedLoadSourceCompleteness": load_completeness,
        "unparsedDistributedLoadDiagnostics": unparsed_loads,
        "sourceGridAudit": source_grids,
        "globalDistributedVectorCandidates": global_vectors,
        "loadSIMagnitudeCandidates": load_si,
        "sourceLoads": {
            "patterns": [{"sourceId": x.source_id, "designType": x.design_type, "selfWeightMultiplier": str(x.self_weight_multiplier), "sourceLine": x.source_line} for x in loads.patterns],
            "jointForces": [{"jointId": x.joint_id, "patternId": x.pattern_id, "coordinateSystem": x.coordinate_system, "components": [str(v) for v in x.components], "sourceLine": x.source_line} for x in loads.joint_forces],
            "distributedFrameLoads": [{"frameId": x.frame_id, "patternId": x.pattern_id, "coordinateSystem": x.coordinate_system, "loadType": x.load_type, "direction": x.direction, "distanceType": x.distance_type, "start": str(x.start), "end": str(x.end), "magnitudeStart": str(x.magnitude_start), "magnitudeEnd": str(x.magnitude_end), "sourceLine": x.source_line} for x in advanced_loads.distributed],
            "loadCases": [{"sourceId": x.source_id, "caseType": x.case_type, "fields": list(x.fields), "sourceLine": x.source_line} for x in advanced_loads.cases],
            "loadCombinations": [{"sourceId": x.source_id, "combinationType": x.combination_type, "terms": [{"referenceId": t.case_or_combo_id, "factor": str(t.factor), "sourceLine": t.source_line} for t in x.terms], "sourceLines": list(x.source_lines)} for x in advanced_loads.combinations],
            "diagnostics": list(loads.diagnostics) + list(advanced_loads.diagnostics),
            "mappedToCore": False,
        },
        "frameLocalAxes": {
            "rotations": [{"frameId": x.frame_id, "angleDegrees": str(x.angle_degrees), "sourceLine": x.source_line} for x in axes.rotations],
            "insertions": [{"frameId": x.frame_id, "fields": list(x.fields), "sourceLine": x.source_line} for x in axes.insertions],
            "diagnostics": list(axes.diagnostics),
            "mappedToCore": False,
        },
        "diaphragmConstraints": {
            "definitions": [{"sourceId": x.source_id, "coordinateSystem": x.coordinate_system, "axis": x.axis, "multiLevel": x.multi_level, "sourceLine": x.source_line} for x in diaphragms.definitions],
            "memberships": [{"jointId": x.joint_id, "diaphragmId": x.diaphragm_id, "sourceLine": x.source_line} for x in diaphragms.memberships],
            "diagnostics": list(diaphragms.diagnostics),
            "mappedToCore": False,
        },
        "engineeringDisposition": {
            "taperedMaterialIdentities": "source-verified",
            "nonprismaticAnalyticalSections": "preserved-not-mapped",
            "explicitNoneAssignments": "preserved-not-substituted",
            "loadsAndCombinations": "source-preserved-not-core-mapped",
            "frameAxesAndInsertions": "source-preserved-not-core-mapped",
            "diaphragmConstraints": "source-preserved-not-core-mapped",
            "otherCoreDomains": "not-validated",
        },
        "canonicalCoreValidated": False,
        "analysisReady": False,
        "coreModel": None,
    }
