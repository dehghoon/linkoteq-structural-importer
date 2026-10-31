# Engineering Extraction Validation Standard

Status: draft v0.1 — applies to SAP2000, ETABS, STAAD.Pro. This document defines required tests, not a claim that they all pass.

## Scope and evidence levels
1. Source fixture integrity: pinned original bytes, SHA-256, provenance, software/version, units, and licensing/permission.
2. Structural parsing: record counts, syntax, continuations, unknown records, diagnostics.
3. Source-to-extractor comparison: independently decode expected values from source and compare all supported IDs, coordinates, connectivity, materials, sections, assignments, restraints, releases, springs, load cases, patterns, loads, combinations, and units. Avoid using the same parsing helper for oracle and implementation; independent reference fixtures or reviewed golden values are preferred.
4. Core mapping: compare canonical units, axes, orientations, end releases, DOFs, load signs, stable IDs and provenance to Core Contract (latest released version).
5. Export fidelity: IFC4 validation, mapped/preserved/omitted classification; round-trip or reference comparison where feasible.
6. Engineering equivalence: only claim after independent model/result comparison with documented tolerances and software versions.

## Mandatory methodology
- Every test specifies input file and SHA, expected output/oracle origin, assertions, tolerances, diagnostic policy, and CI evidence link.
- Use exact comparison for identifiers, connectivity, categorical assignments, and unconverted decimal source values.
- Use explicit dimension-specific tolerances for numerical transformations; never silently round, invent defaults, or silently drop records.
- Fail on missing/duplicate source identifiers, unexpected unsupported semantics, wrong unit conversion, unreported information loss, or incorrect reference relationships.
- Preserve original source bytes and unrecognized commands independently of successful interpretation.
- Report separately: preserved, parsed, validated, mapped to Core, visualized, IFC-exported, analysis-supported, equivalence-verified.
- Negative fixtures: duplicate IDs, missing references, malformed numbers, encoding changes, unit changes, coordinate systems, local axes, releases, and unsupported features.
- CI must show PASS/FAIL/SKIP/NOT_IMPLEMENTED per capability and software. SKIP is not PASS.
- Review any independent oracle against original application export or a manually verified sample; independent text parsing alone does not prove engineering equivalence.

## Format-specific adapters
- SAP2000: .s2k / .$2k tables, continuations, XorR, PROGRAM CONTROL, unit declarations, local axes and coordinate systems.
- ETABS: .e2k / .$et, stories, levels, diaphragms, element assignments and coordinate transforms.
- STAAD.Pro: .std / .sbk, command continuation, semicolons, TO ranges, unit changes, member selections, support and release semantics, SRSS versus linear combinations.

## Shared test contract
Each format adapter must produce a comparable typed source view with source_id, source_line, source_hash, raw source reference, units, values, and diagnostics. Generic assertions consume this view; format-specific tests validate parsing and semantics.

## Current evidence and gaps (2026-10-31)
- SAP2000 real fixture: docs/MTDENN~1.$2k; earlier smoke tests checked 388 joints, 609 frames, 84 sections, source SHA and referential integrity.
- scripts/test_sap2000_exact_geometry_fixture.py added to compare every extracted joint coordinate and frame endpoint to independently parsed source records. CI result must be verified before marking PASS.
- The independent comparison still shares a similar field grammar and is not an independent SAP2000 application oracle; it does not prove Core/IFC equivalence.
- ETABS and STAAD-Pro corresponding engineering comparison tests are NOT_IMPLEMENTED.
- Material, section, boundary, and load numeric golden-value comparisons are NOT_IMPLEMENTED for SAP2000.

## Execution sequence
1. Verify SAP2000 exact-geometry CI result and fix failures.
2. Add independently reviewed golden values and negative tests for SAP2000 geometry, then properties, boundaries, loads, and unit conversions.
3. Extract reusable typed comparison helpers; maintain source-specific adapters.
4. Repeat source-to-extractor and negative tests on ETABS and STAAD fixtures.
5. Add Core mapping and IFC comparison only after source semantics are validated.

No merge to main solely on smoke-test success.
