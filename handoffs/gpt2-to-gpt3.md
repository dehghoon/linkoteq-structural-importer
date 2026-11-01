# GPT-2 → GPT-3: Import Result v0.1.0 candidate (NOT MERGED)

Baseline: Structural Core released tag v0.5.0; merged Core Gap Register `docs/CORE_GAP_REGISTER.md` remains OPEN, no Core schema revision authorized. 3D Model PR #5 and Core PR #5 have been verified merged; importer PR #2 remains draft.

## Candidate producer
`linkoteq_importer.import_result.build_import_result(archive, format=..., limits=...)`

The importer-owned transport envelope is `contract=linkoteq.import-result`, `version=0.1.0`, `coreContract=v0.5.0`. It includes `source` (archive hash, byte count, filename), `sourceViews`, `stages`, `capabilities`, `diagnostics`, `fidelity`, and `coreModel=null`.

- SAP2000: source-view joints/frames, materials/sections, frame section assignments, restraints, springs, releases, patterns, nodal loads, selected distributed loads, cases, combinations. Diaphragm definitions and joint memberships are now extracted into source views; no Core promotion or rigid/semi-rigid behavioral equivalence claim. Unsupported distributed-load variants remain in source archive with diagnostic, not interpreted as zeros.
- STAAD: source-view nodes/frames via existing lexical and geometry parser, explicit units retained per node. Other engineering features preserved-only.
- ETABS: preservation-only; engineering parser not connected. No invented nodes, members or property values.
- Stable IDs use existing `entity_id` algorithm with namespace, source profile, entity kind and source identifier; repeated assignment/load records use source line plus record ordinal scope.
- All numeric source values are strings in the transport (exact Decimal string where available). No implicit SI conversion; no Core canonical model is asserted.
- The original bytes are retained independently of parsing; an archive receipt is **not** evidence of equivalent engineering conversion.

## GPT-3 consumer guidance
Treat `sourceViews` as read-only importer evidence and a partial preview, **not** as a validated Structural Core model. Do not directly use source-coordinate values as canonical SI geometry unless explicit unit validation/conversion has passed. Use the existing Core-backed manual model and its editors independently of import. Show preserved/unsupported/unmapped features and source provenance. Do not map SRSS/modal combinations to linear sums.

## Integration gate
Agree on JSON schema, capability states, byte provenance for records, unit conversion/orientation, diaphragm semantics and security/auth boundaries. Only promote `coreModel` when mapping and Core validation pass. Test SAP, ETABS and STAAD samples and regression CI; avoid claiming readiness from the partial contract.

## Diaphragm regression (2026-11-01)
SAP2000 source tables `CONSTRAINT DEFINITIONS - DIAPHRAGM` and `JOINT CONSTRAINT ASSIGNMENTS` now feed `sourceViews.diaphragms` and `sourceViews.diaphragmMemberships`. Verified GitHub Actions PASS: https://github.com/dehghoon/linkoteq-structural-importer/actions/runs/41310243381 . Area membrane sections are separate and not inferred to be diaphragm constraints. Source joint IDs and source line provenance are retained. Consumer must not treat source view as a Core diaphragm until contract semantics are validated.

## Source reference validation (2026-11-01)
`Import Result.referenceAudit` reports source-reference diagnostics for restraints, springs, end releases, nodal loads, distributed frame loads, and diaphragm memberships. No repair/defaulting is performed. CI PASS on real pinned SAP fixture and synthetic invalid references: https://github.com/dehghoon/linkoteq-structural-importer/actions/runs/41310588128 . This validates identifier existence only, not member local-axis semantics, units, Core schema, or structural analysis equivalence.

## Frame local-axis source views (2026-11-01)
SAP2000 `FRAME LOCAL AXES ASSIGNMENTS 1 - TYPICAL` and `FRAME INSERTION POINT ASSIGNMENTS` now feed `sourceViews.frameAxisRotations` and `sourceViews.frameInsertions`. CI PASS: https://github.com/dehghoon/linkoteq-structural-importer/actions/runs/41310751406 . Angles remain source degrees; insertion fields remain original key/value pairs. End-release DOF flags remain in source-local semantics, NOT global/ Core transformed. GPT-3 must not infer local 2/3 direction or pinned behavior without validated member axis transformation.
