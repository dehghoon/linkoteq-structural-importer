# SAP2000 → Core v0.6 migration gate (GPT-2)

Status: IN PROGRESS — NOT CORE-VALIDATED. Branch: `gpt2/core-v06-sap-migration`.

## Current contract boundary

The producer still emits `linkoteq.import-result` v0.1.0 with legacy `coreContract: v0.5.0` and `coreModel: null`. The added `targetCoreContract: v0.6.0` expresses the migration target only; `coreMappingStatus: not-validated` is mandatory. Do not consume `sourceViews` as canonical Core or as analysis-ready geometry. Original source bytes remain independently archived.

## Required gates before promotion

1. Pin the official Core v0.6.0 tag and locate its actual machine validator; validate a full canonical model with the official implementation, not just a JSON envelope.
2. Resolve every frame's material and section references without invented defaults; preserve unresolved designations with source identifiers and diagnostic status.
3. Convert source dimensions and load magnitudes with explicit unit evidence; fail closed for ambiguous or changing source units.
4. Validate right-handed I→J local axes, angle sign, end releases including partial stiffness, insertion offsets and cardinal points against source evidence.
5. Preserve diaphragm constraints and membership separately from surface membranes; do not silently turn semi-rigid into rigid.
6. Audit nodal, frame point/distributed, surface and self-weight loads and combinations. Preserve modal/SRSS semantics rather than treating them as linear sums.
7. Run the real SAP2000 fixture through both source-lexical checks and a complete source→Core conversion; compare counts, identities, units, forces, moments and unconverted records.
8. Emit a per-record fidelity report: mapped, preserved-only, unsupported, invalid, with source hash, source line, original IDs, units and diagnostics.
9. Deliver a Core-validator PASS artifact and regression output to GPT-3. No UI, viewport or PyNite work is included here.

## Existing reusable implementation

Use `sap2000_geometry.py`, `sap2000_properties.py`, `sap2000_boundary.py`, `sap2000_frame_axes.py`, `sap2000_release_semantics.py`, `sap2000_diaphragms.py`, `sap2000_advanced_loads.py`, `core_geometry_fragment.py` and the source archive. Incorporate the real-fixture lexical regression from `gpt2/sap2000-real-fixture-regression` without conflating lexical checks with structural conversion.

## Acceptance status

Current status is **BLOCKED** for a complete canonical Core v0.6 model. The new target/version checks are transport-level safety guards, not engineering conversion. CI results must be linked before claiming tests passed.
