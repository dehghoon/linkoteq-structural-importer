# Linkoteq Universal Structural Model Importer — initial engineering package

Version 0.1.0-draft, 2026-10-28. Authored specifications, not a working importer. All engineering profiles require the stated verification gates. Start with docs/IMPORTER_ENGINEERING_SPEC.md, docs/REPOSITORY_INSPECTION.md and handoffs/gpt1-to-gpt2.md.

The nine requested specification documents plus GPT-1 handoff are provided. Supporting repository evidence and project status record unresolved release/units/semantics/integration questions. No Core schema change, parser, private sample or downstream agent-completion handoff is included.

Published initial package: commit `66675d5158000aaca4ffe80f2efc08504d2bdd44` on `main`. All 13 published files were read back and matched the approved contents. No workflow runs were found for that commit; no parser, IFC artifact or deployment is claimed.

Next: GPT-2 implements the source-preservation infrastructure in docs/INITIAL_IMPLEMENTATION_CONTRACT.md. See handoffs/gpt1-to-gpt4.md for unresolved integration decisions. Publication approval is recorded; engineering approvals and capability gates remain separate.

## CSI amendment 0.1.1-draft
ETABS 13.2.2 and SAP2000 19.0.0 private samples have been inventoried. See docs/CSI_SAMPLE_COVERAGE_AUDIT.md, parser section 9 and CSI-01–CSI-13 acceptance cases. The initial infrastructure work package and publication-status correction are included in the same amendment. File preservation is required; complete source-to-Core engineering conversion remains unverified.

## Structural Core compatibility target (Revision 6)

Canonical contract: [Linkoteq Structural Core](https://github.com/dehghoon/linkoteq-structural-core/blob/main/CORE_CONTRACT.md).

- Target Core package: `v0.6.0`; target model schema: `0.6`.
- Legacy model schema `0.5` remains supported at the Core contract boundary.
- This declaration is a migration target, not proof that this repository's runtime dependency, API, importer mapping, or deployment has migrated.
- Existing engineering calculation and application behavior is unchanged by this documentation update.
- The Core `v0.6.0` GitHub Release must be verified separately from the version on `main`.
