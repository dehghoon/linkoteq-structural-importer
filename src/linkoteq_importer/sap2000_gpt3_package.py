"""Lossless, non-certified SAP2000 handoff for the Advanced Model viewport.

This transport is NOT a canonical Core v0.6 StructuralModel. The source
archive is included verbatim as base64 for full fidelity.
"""
from __future__ import annotations

from base64 import b64encode
from decimal import Decimal
from json import dumps
from typing import Any

from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_properties import extract_properties
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.partial_structural_model import build_partial_model
from linkoteq_importer.sap2000_v06_gate import build_sap2000_v06_gate_report

DEFAULT_LIMITS = Limits(20_000_000, 200_000, 200_000, 2_000_000,
                        200_000, 300_000, 300_000, 100_000_000)


def _number(value: Decimal) -> float:
    if not value.is_finite():
        raise ValueError("NONFINITE_SOURCE_COORDINATE")
    return float(value)


def build_gpt3_package(data: bytes, *, filename: str, project_id: str,
                       limits: Limits = DEFAULT_LIMITS) -> dict[str, Any]:
    """Build a source-preserving viewport package without certifying Core mapping.

    Inputs: raw SAP2000 bytes, original filename, stable project ID.
    Coordinates retain source units; the UI must not assume SI conversion.
    All engineering source records remain in importFidelity/sourceArchive.
    """
    if not filename.lower().endswith((".s2k", ".$2k")):
        raise ValueError("UNSUPPORTED_SAP_EXTENSION")
    if not project_id:
        raise ValueError("PROJECT_ID_REQUIRED")
    extension = ".$2k" if filename.lower().endswith(".$2k") else ".s2k"
    archive = archive_bytes(data, filename=filename, extension=extension,
                            project_ref=project_id, namespace="sap2000",
                            policy_id="preserve-source", limits=limits)
    geometry = extract_geometry(archive)
    properties = extract_properties(archive)
    boundaries = extract_boundaries(archive)
    partial = build_partial_model(geometry, properties, stress_unit="kPa",
                                  density_unit="kg/m3", length_unit="m")
    gate = build_sap2000_v06_gate_report(partial, geometry, boundaries,
                                        project_id=project_id, archive=archive,
                                        properties=properties)
    joints = {j.source_id: j for j in geometry.joints}
    nodes = [{"sourceId": j.source_id,
              "position": {"x": _number(j.x), "y": _number(j.y), "z": _number(j.z)},
              "sourceLine": j.source_line} for j in geometry.joints]
    members = [{"sourceId": f.source_id, "startNodeId": f.joint_i,
                "endNodeId": f.joint_j, "sourceLine": f.source_line,
                "renderable": f.joint_i in joints and f.joint_j in joints}
               for f in geometry.frames]
    z_values = sorted({j.z for j in geometry.joints})
    inferred_levels = [{"id": f"inferred-z-{i}", "name": f"Elevation {z}",
                        "elevation": _number(z), "provenance": "inferred-from-node-z",
                        "sourceDefined": False} for i, z in enumerate(z_values)]
    fidelity = gate["importFidelity"]
    if fidelity is None:
        raise ValueError("MISSING_IMPORT_FIDELITY")
    return {
        "format": "linkoteq-sap2000-gpt3-handoff-v1",
        "targetCoreSchemaVersion": "0.6",
        "sourceHash": archive.sourceHash,
        "coreModel": gate["coreModel"],
        "coreMappingStatus": gate["status"],
        "canonicalMappingValidated": False,
        "analysisReady": False,
        "geometryPreview": {
            "sourceUnits": geometry.declared_units,
            "coordinateSystem": "GLOBAL",
            "coordinatesConvertedToSI": False,
            "nodes": nodes,
            "members": members,
            "grids": fidelity["sourceGridPreview"],
            "sourceLevels": fidelity["sourceLevelAudit"],
            "inferredLevels": inferred_levels,
            "propertyAssignments": partial["members"],
            "sectionProperties": partial["sectionProperties"],
            "materialProperties": partial["materialProperties"],
        },
        "engineeringData": {
            "sourceLoads": fidelity["sourceLoads"],
            "sourceSupportMapping": gate["sourceSupportMapping"],
            "sourceReleaseMapping": gate["sourceReleaseMapping"],
            "frameLocalAxes": fidelity["frameLocalAxes"],
            "diaphragmConstraints": fidelity["diaphragmConstraints"],
        },
        "sourceArchive": {
            "filename": filename, "extension": extension,
            "sha256": archive.sourceHash, "byteLength": archive.byteLength,
            "encoding": "base64", "bytesBase64": b64encode(archive.retrieve()).decode("ascii"),
        },
        "importFidelity": fidelity,
        "diagnostics": {
            "geometry": list(geometry.diagnostics),
            "mapping": gate["geometryProperties"].get("diagnostics", []),
            "blockers": gate["blockers"],
        },
        "sourceToCoreIds": {"status": "not-certified", "mapping": {}},
    }


def package_to_json(package: dict[str, Any], *, indent: int | None = 2) -> str:
    """Serialize the complete handoff without silently dropping source fields."""
    def encode(value: object) -> object:
        if isinstance(value, Decimal):
            if not value.is_finite():
                raise ValueError("NONFINITE_ENGINEERING_VALUE")
            return str(value)
        raise TypeError(f"NON_JSON_HANDOFF_TYPE:{type(value).__name__}")

    return dumps(package, ensure_ascii=False, indent=indent, default=encode, allow_nan=False)
