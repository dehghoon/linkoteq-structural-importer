# PARALLEL IMPLEMENTATION PLAN

Version: 0.1.0-draft | 2026-10-28 | Owner: GPT-1 | Engineering review pending

Core target: 0.5 at b1f25a6b735f4e3c586d4d8497298ebd6f656126. This is an inspected main snapshot, NOT a verified release.

| Workstream | Owner | Permitted now | Blocking promotion dependency |
|---|---|---|---|
| Immutable archive/spans/diagnostics/identity | GPT-2 | implement initial infrastructure contract after document review | limits/retention for deployment |
| STAAD parser | GPT-2 | synthetic profile and source-IR prototypes | grammar/units/axes/catalog/SRSS semantics reviewed per feature |
| ETABS and SAP parsers | GPT-2 | fixture procurement and independent profile prototypes | source version evidence, licensing, golden comparisons |
| Core baseline/gaps | GPT-4 with GPT-1 | resolve release and unit/density decisions | no unreviewed Core changes |
| Job API/UI/source inspection | GPT-3 | mocks, progress states, diagnostics UX | stable published API and verified engine |
| 3D integration | GPT-3 | trace active code, pin reconciliation, contract tests | no inferred defaults or independent engineering interpretation |
| IFC | GPT-3 | library/license evaluation and synthetic prototype | reviewed IFC mapping, unit boundary, independent validation |
| Security | GPT-5 coordinated by GPT-4 | threat model upload/storage/job/access | high/critical findings block release absent scoped authorized exception |
| Product/website | GPT-4/GPT-3 | nonfunctional tool positioning/discovery | actual validated capability claims and entitlement decision |

## Provisional API v0.1.0
POST /imports accepts uploaded object reference, project/model namespace, profile hint and policy version; returns job ID. GET /imports/{id} reports queued/archiving/detecting/parsing/validating/mapping/completed/failed/cancelled, result availability and authorized links. POST /imports/{id}/exports creates a separately tracked IFC export after eligibility validation. DELETE /imports/{id} requests policy-governed deletion. These are proposed routes, not existing deployed endpoints. No signed source URL in public logs. Idempotency key scope includes owner/project/source hash/options; differing options with reused key cause conflict. Worker enforces wall/CPU/memory/expansion limits; cancellation is cooperative plus isolation termination. Versioned output conforms to IMPORTER_ENGINEERING_SPEC, not a duplicate Core schema.

## Delivery contracts
GPT-2 handoff must include engine API, Core pin, all fixture hashes/permissions, test logs, runtime/dependency pins, limits, known partial mappings and fidelity examples. GPT-3 handoff must add API authentication/authorization evidence, viewer feature matrix, IFC validation/reimport, deployment IDs, health/smoke evidence and blockers. Do not write completed GPT-2/GPT-3 handoffs on their behalf. GPT-4 records approvals per capability and source version. Keep downstream release blockers visible even when upstream preservation is ready.

## Repository coordination
The independent public repository dehghoon/linkoteq-structural-importer is now verified accessible, with pull/push permissions reported. Main ref retrieval returned HTTP 409, Git Repository is empty. No base commit exists. Publish this package at repository root, without modifying Core. The original temporary Core location proposal is superseded. Exact initial diff approval is required by the invoked plugin skill. Initialize README.md first through the contents API, then publish remaining documents against the observed initialization commit; verify both commits and all contents. No force update or additional branch is authorized.
