"""Strict, vendor-neutral Import Result v0.1.0 consumer boundary.

Checks transport shape and provenance, NOT structural equivalence.
Never promotes sourceViews to a canonical Core model.
"""
from __future__ import annotations

FORMATS = frozenset(("sap2000", "etabs", "staad"))
DOFS = ("U1", "U2", "U3", "R1", "R2", "R3")
SOURCE_VIEW_KEYS = (
    "nodes", "frames", "materials", "sections", "frameSectionAssignments",
    "restraints", "springs", "releases", "loadPatterns", "nodalLoads",
    "distributedFrameLoads", "loadCases", "loadCombinations",
    "diaphragms", "diaphragmMemberships", "frameAxisRotations",
    "frameInsertions", "frameEndReleaseSemantics",
)

class ImportResultContractError(ValueError):
    pass

def validate_import_result(result: dict) -> tuple[str, ...]:
    """Reject malformed envelopes; return non-fatal engineering limitations."""
    def require(condition: bool, code: str) -> None:
        if not condition:
            raise ImportResultContractError(code)

    require(isinstance(result, dict), "RESULT_NOT_OBJECT")
    require(result.get("contract") == "linkoteq.import-result", "UNKNOWN_CONTRACT")
    require(result.get("version") == "0.1.0", "UNSUPPORTED_VERSION")
    require(result.get("coreContract") == "v0.5.0", "UNSUPPORTED_CORE_BASELINE")
    require(result.get("sourceFormat") in FORMATS, "UNKNOWN_SOURCE_FORMAT")
    source = result.get("source")
    require(isinstance(source, dict), "SOURCE_NOT_OBJECT")
    require(isinstance(source.get("sourceHash"), str) and len(source["sourceHash"]) == 64,
            "SOURCE_HASH_MISSING")
    require(source.get("archiveAvailable") is True, "SOURCE_ARCHIVE_NOT_AVAILABLE")
    views = result.get("sourceViews")
    require(isinstance(views, dict), "SOURCE_VIEWS_NOT_OBJECT")
    for name in SOURCE_VIEW_KEYS:
        require(isinstance(views.get(name), list), "SOURCE_VIEW_INVALID:" + name)
    require(result.get("coreModel") is None, "UNVERIFIED_CORE_MODEL_MUST_BE_NULL")
    require(isinstance(result.get("stages"), dict), "STAGES_NOT_OBJECT")
    require(isinstance(result.get("capabilities"), dict), "CAPABILITIES_NOT_OBJECT")
    require(isinstance(result.get("diagnostics"), list), "DIAGNOSTICS_NOT_LIST")
    require(isinstance(result.get("fidelity"), dict), "FIDELITY_NOT_OBJECT")
    require(result["fidelity"].get("originalBytesPreserved") is True,
            "SOURCE_PRESERVATION_NOT_VERIFIED")
    require(result["fidelity"].get("engineeringEquivalenceVerified") is False,
            "ENGINEERING_EQUIVALENCE_NOT_VERIFIED")
    warnings = []
    for index, item in enumerate(views["frameEndReleaseSemantics"]):
        prefix = "RELEASE_SEMANTICS:" + str(index) + ":"
        require(isinstance(item, dict), prefix + "NOT_OBJECT")
        require(isinstance(item.get("frameSourceId"), str) and bool(item["frameSourceId"]),
                prefix + "FRAME_MISSING")
        for end in ("startReleaseLocal", "endReleaseLocal"):
            values = item.get(end)
            require(isinstance(values, dict) and set(values) == set(DOFS),
                    prefix + end + ":DOF_KEYS")
            require(all(type(values[k]) is bool for k in DOFS),
                    prefix + end + ":DOF_VALUES")
        require(item.get("status") == "source-local-interpretation-not-core-mapped",
                prefix + "UNVERIFIED_STATUS")
        angle = item.get("localAxisAngleDegrees")
        require(angle is None or isinstance(angle, str), prefix + "ANGLE_NOT_SOURCE_STRING")
        if angle is None:
            warnings.append(prefix + "AXIS_ROTATION_NOT_EXPLICIT")
    return tuple(warnings)
