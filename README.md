# Linkoteq Universal Structural Model Importer — initial engineering package

Version 0.1.0-draft, 2026-10-28. Authored specifications, not a working importer. All engineering profiles require the stated verification gates. Start with docs/IMPORTER_ENGINEERING_SPEC.md, docs/REPOSITORY_INSPECTION.md and handoffs/gpt1-to-gpt2.md.

The nine requested specification documents plus GPT-1 handoff are provided. Supporting repository evidence and project status record unresolved release/units/semantics/integration questions. No Core schema change, parser, private sample or downstream agent-completion handoff is included.

Published initial package: commit `66675d5158000aaca4ffe80f2efc08504d2bdd44` on `main`. All 13 published files were read back and matched the approved contents. No workflow runs were found for that commit; no parser, IFC artifact or deployment is claimed.

Next: GPT-2 implements the source-preservation infrastructure in docs/INITIAL_IMPLEMENTATION_CONTRACT.md. See handoffs/gpt1-to-gpt4.md for unresolved integration decisions. Publication approval is recorded; engineering approvals and capability gates remain separate.

## CSI amendment 0.1.1-draft
ETABS 13.2.2 and SAP2000 19.0.0 private samples have been inventoried. See docs/CSI_SAMPLE_COVERAGE_AUDIT.md, parser section 9 and CSI-01–CSI-13 acceptance cases. The initial infrastructure work package and publication-status correction are included in the same amendment. File preservation is required; complete source-to-Core engineering conversion remains unverified.

## Required validation contract for all importer development

**Before changing a parser, adding a fixture, implementing a new format, or claiming a capability is verified, read and follow:**

- [Importer Validation Contract](docs/IMPORTER_VALIDATION_CONTRACT.md) — shared acceptance levels, mandatory comparisons, evidence, regression and documentation-update requirements for SAP2000, ETABS and STAAD.Pro.
- [Engineering Extraction Validation Standard](docs/ENGINEERING_EXTRACTION_VALIDATION_STANDARD.md) — format-specific engineering checks and current gaps.
- [Fixture manifest template](docs/fixtures/validation-case-template.json) — copy for each pinned real or synthetic fixture; record source SHA, expected values, oracle, tolerance and CI run.

**Required PR checklist:** (1) add/update a fixture manifest and independently reviewed expected values, (2) add or update regression tests and negative cases, (3) record PASS/FAIL/SKIP/NOT_IMPLEMENTED per capability with CI evidence, (4) update the validation contract if shared rules change, (5) identify affected SAP2000/ETABS/STAAD tests. A passing smoke test is not engineering equivalence. Documentation alone does not mean these gates have passed.

The linked documents currently live on the SAP2000 development branch and must be included in the PR merge to make this guidance available on `main`.
