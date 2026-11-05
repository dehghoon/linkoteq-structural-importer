# GPT-2 → GPT-3: SAP2000 3D preview integration handoff (draft)

Status: **PREVIEW CONTRACT AVAILABLE / NOT A CORE v0.6 ANALYTICAL HANDOFF**.

Source of truth: importer branch `gpt2/core-v06-sap-migration`; real fixture `docs/MTDENN~1.$2k` (SHA256 `8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79`).

## What GPT-3 may integrate now

1. Read source archive via `preservation.archive_bytes`; use `sap2000_geometry.extract_geometry` for joints/frames and `sap2000_properties.extract_properties` for section/material source labels.
2. Render **source-geometry preview only**, preserving original joint/frame IDs and original section designations. The real fixture contains 388 joints and 609 frames.
3. Display unresolved member sections as **unresolved**, not as an invented default. Four assignments refer to `None`; nonprismatic `Tapered Beam` is not an analytical Core section.
4. Keep original archive bytes, source hash, provenance, and the complete `importFidelity` report associated with the preview. The parser now extracts 1,810 distributed load records: 1,614 forces plus 196 distributed moments; parsing is **not** Core load mapping.
5. Make all non-certified domains visible as preserved metadata or warnings; do not imply analysis validity.

## Integration guardrails

- `build_sap2000_v06_gate_report(...)` returns `coreModel=None`, `canonicalMappingValidated=False`, `analysisReady=False` for the fixture. **Do not bypass this gate** or pass the geometry preview to PyNite/analysis.
- `core_v06_candidate.project_geometry_properties_v06` is deliberately blocked on unresolved engineering references. Do not synthesize a canonical Core model by dropping blockers.
- Do not silently replace unknown sections, reinterpret local axes, apply insertion offsets, or rotate loads.
- Keep 3D preview separate from analytical Core import. Provide UI badges/status: `Source preview — not analysis ready`, unresolved section warnings, and import-fidelity link.
- Selection/editing must retain stable source identifiers; source archive remains immutable. Any editing is a new derived model with explicit provenance.

## Acceptance tests for GPT-3

- Fixture renders exactly 388 joints and 609 source frames, with stable IDs and coordinates.
- Four unknown section assignments and tapered/nonprismatic section appear as unresolved; no default analytical section silently substituted.
- Archive hash matches pinned SHA256; raw source and Import Fidelity can be retrieved.
- 1,810 distributed loads remain traceable (including 196 Moment); no unsupported load is displayed as an analytical Core load.
- Import preview does not expose an analysis-ready or validated Core model.
- UI/viewport work belongs to GPT-3; GPT-2 owns importer and semantic Core mapping.

## Remaining GPT-2 work

Formal Core v0.6 validator integration, insertion offsets, frame local axes, diaphragms, distributed force/moment direction semantics, releases, section/material reconciliation, STAAD and ETABS parity. A **second, canonical-model handoff** follows only after validator PASS on a real fixture.
