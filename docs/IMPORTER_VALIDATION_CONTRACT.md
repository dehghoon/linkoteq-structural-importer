# Linkoteq Importer Validation Contract

Contract version: 0.1.0 (draft) | Updated: 2026-10-31 | Owner: GPT-2 (engine), reviewed by GPT-1 (spec) and GPT-4 (integration)
Applies to SAP2000, ETABS and STAAD.Pro; every future supported format must implement this contract.

## Purpose and invariants
Fixtures are **examples**, not proof of general format coverage. Separate the immutable test methodology from versioned source-specific cases. Preserve original bytes and provenance even when parsing fails. Never silently invent defaults or drop unsupported semantics. Never call a smoke test engineering equivalence.

## Evidence ladder
E0: original bytes, SHA256, provenance and access verified.
E1: structural record parsing and syntax diagnostics.
E2: exact source-to-extractor field comparisons for supported semantics.
E3: validated units, axes, loads, releases, sections and source-specific meaning against reviewed independent oracle.
E4: mapped-to-Core values and traceability verified against released Core Contract.
E5: IFC/export verification and explicit fidelity/omission report.
E6: independent engineering-equivalence tests (where applicable).
Each capability reports PASS, FAIL, SKIP, NOT_IMPLEMENTED or BLOCKED **at its own level**. Passing E1 does not imply E2-E6.

## Required fixture manifest
Use the companion `docs/fixtures/validation-case-template.json` for each fixture:
format, source_application/version, source_file, sha256, encoding, declared/changed units, source license/access, expected entities/fields, expected diagnostics, independent oracle method, numerical tolerance by dimension, supported capability level, CI command and run URL.
Record source line/byte offsets and original IDs where available. Pin source commit and extractor commit.

## Required comparisons
- All joint IDs and X/Y/Z; frame IDs, I/J connectivity, local axes, offsets and level/story relationships.
- Materials: names, units, E/G/nu/density/strength and modifiers; sections: catalog/custom geometry, orientation, assignments.
- Boundary: all six DOFs, springs, releases, constraints and coordinate-system transforms.
- Loads: patterns, cases, combinations (including modal/SRSS semantics), self-weight, nodal/member/surface load values, positions, signs and axes.
- Every source record must be classified as mapped, preserved-only, unsupported or invalid, with diagnostics and fidelity report.
- Exact equality for identifiers, categorical fields and source Decimal values. Unit-converted quantities use reviewed dimension-specific tolerances and documented conversion factors.
- A second implementation using similar regex is a cross-check, not an independent ground truth. Use manually reviewed golden values, vendor application export, or another validated reference where possible.

## Mandatory negative/metamorphic tests
Missing/duplicate IDs; dangling references; corrupt encoding; multiline/continuation syntax; unexpected tables; mixed unit changes; local/global axes; reordered records; malformed numbers; unsupported feature preservation; incorrect release/load direction. Verify intended failure and error codes. Include small synthetic known-answer fixtures and real-world samples.

## CI gates
- PR: parser unit tests, synthetic golden tests, all accessible pinned real-fixture regressions, source preservation and diagnostics; publish machine-readable results and summary.
- Format readiness: no required E2/E3 failures; all unsupported features explicitly classified; Core integration requires E4; public export claims require E5.
- Never turn a missing fixture or unimplemented capability into PASS. Keep fixture SHA pinned; update only via reviewed change.
- Changes to parser, Core adapter, fixture, units or semantics must trigger affected suites; record why any assertion changes.

## Reuse procedure for next format
1. Copy fixture manifest; pin raw source and reference values.
2. Implement format-specific tokenizer/parser to shared typed source view (source ID, raw source reference, units, provenance, diagnostics).
3. Reuse generic identity, coordinate, connectivity, numeric, classification and fidelity assertions.
4. Add format-specific semantics: SAP2000 S2K/$2k tables and continuations; ETABS E2K/$et stories/diaphragms; STAAD STD/SBK command syntax, unit switches, ranges and SRSS.
5. Run synthetic, negative and real-fixture suites, log coverage and unresolved gaps; only then advance Core mapping.

## Continuous documentation rule
For every PR that changes parser behavior or discovers a new format case: update this contract only if shared rules change; otherwise add/update a fixture manifest and format-specific case note. Record discovery, original example, expected/actual, resolution, regression test, evidence URL and affected formats. Review contract version changes with GPT-1/GPT-4; no automatic assumption of approval.

## Current status at contract creation
SAP2000: structural and basic engineering extraction smoke tests exist. Exact geometry source comparison was added; its CI result is not asserted here. No independent vendor oracle, full load/section semantics, Core mapping or IFC equivalence is verified.
ETABS and STAAD.Pro: comparable contract-based engineering suites are not yet implemented.
This contract is documentation, not evidence of completed tests.

## Risk-based sample selection policy

The normative project policy for choosing independently reviewed golden samples across all eight engineering domains and SAP2000/ETABS/STAAD.Pro is [RISK_BASED_VALIDATION_SAMPLING_STANDARD.md](RISK_BASED_VALIDATION_SAMPLING_STANDARD.md). It defines mandatory risk classes, deterministic minimum counts and reporting requirements. Full-record automated checks remain required; manual sample selection is not a substitute. The sampling engine is not yet implemented and must not be marked PASS solely because this document exists.

## Updated priority decision (2026-10-31)

See [SOURCE_VERSION_AND_CORE_FIRST_POLICY.md](SOURCE_VERSION_AND_CORE_FIRST_POLICY.md). Vendor-source compatibility checks are a **lightweight input gate**, not the primary validation workload. The principal engineering acceptance gate is **E4 source-to-Core semantic mapping**; E2 extraction regressions remain useful but do not constitute Core verification. Risk-sample selection tools remain optional diagnostics, not release-blocking evidence of mapping correctness. No unsupported numeric version cutoff may be invented. Existing E0-E3 and preservation safeguards remain in effect; the change is priority and scope, not permission to silently lose data.
