# Repository inspection and evidence register

Date: 2026-10-28. Reads used connected GitHub; primary source refs were main, followed by pinned verification of Core contract/types and 3D package/status. File blob SHA is not a commit SHA. Main snapshots can move after this inspection.

| Repository | Observed main commit | Result |
|---|---|---|
| dehghoon/linkoteq-structural-core | b1f25a6b735f4e3c586d4d8497298ebd6f656126 | Contract and TypeScript declare 0.5; releases [] and git/matching-refs/tags [] |
| dehghoon/3D-Model | 37fb0dc736ed2acffb8619b70ad7e585614642f1 | package/status dependency mismatch; production status REBUILD_PENDING |
| dehghoon/Main-website | 8ee7c7e1795f0fa1c24b5bbd9f69c97f669eb448 | README read; main commits trigger production deployments per documentation, not independently tested here |

Core releases endpoint returned no releases; tags endpoint was unsupported by fetch, so Git matching-refs/tags was read successfully and returned empty. Thus no latest released Core version is established. v0.5 is the observed main contract, not a fabricated tagged release. GPT-4 must resolve the authoritative baseline before engineering promotion.

## Core source register
All paths relative to https://github.com/dehghoon/linkoteq-structural-core/blob/b1f25a6b735f4e3c586d4d8497298ebd6f656126/

| Path | Observed blob SHA | Use |
|---|---|---|
| CORE_CONTRACT.md | 5b88c1c5c3049f81915f4772b94e8e617989f05b | Canonical semantics; pinned reread verified |
| typescript/index.ts | fbf75ec50ed9e62d3424e63e6acf82bcae0c439e | Exact type fields; pinned reread verified |
| knowledge/GPT1_SPEC_RULES.md | 51dc2c3d352de90b1de4020ac3f146d3cee387d8 | GPT-1 specification requirements |
| knowledge/GPT1_ENGINEERING_EXTRACTION_MANUAL.md | 551ebf8378aa29d89bc9ccd16195a279cf6d0690 | 15 sections, uncertainty and review rules |
| knowledge/GPT1_CALCULATION_REPORT_GUIDELINE.md | 69c6ec1119aa06fcc0acc90f70bee5564ef1b279 | Report traceability and safety visibility |
| AI_GPT_UPDATE_POLICY.md | 14bf05b264149f2d952f705bf43327221b193a5f | Version/migration ownership |
| knowledge/PLATFORM_ARCHITECTURE.md | 01fc6afd99b222dfe5130962c66fa30c8fbc7ea4 | Cross-product boundary |
| README.md | f6a4d8a70548cc6f6e8b4fd9ce92cd4fc2a3cf20 | Declared schema; adapter documentation conflict |
| adapters/pynite/MAPPING.md | 2b8f52028c1c9a32ff692544e4bf5b279520a1b3 | Adapter requirements; not evidence of runtime completeness |

Recursive tree inspected for schema/migration/tests. No dedicated Core v0.4→v0.5 migration document was established from that inventory. TypeScript is the exact integration field source. Existing `tests` entries in the inspected Core tree are GPT direct-write documents, not evidence of comprehensive engineering tests. Do not infer CI from file presence.

## Integration evidence
3D package blob ef7f813e81a4bf929c7a9d7f176b2f1cd5bf0b0c pins Core 49c0973bd15f6f725e251612785e6f55ff4fede4. Status blob 548fde74ee30991d68986d5299b9573bc44863bb instead records a7c7103e46bb98035d907624b92ff8c21931f496. Both verified at observed 3D main. Status reports historical CI run 94 / head f73c581aa42bcffb060fced9eef1230c2e32a2b6, not current-head CI proof. Its production rebuild and smoke-test blockers remain stated, not independently retested.

lib/core-v05.ts inspected: validates required properties/references and includes legacy migration. This is not automatically an importer validator for arbitrary vendor semantics. lib/visualization/core-scene.ts inspected: display coordinate swap and generic member boxes; active later viewer selection not traced. Repository has multiple renderer revisions, so avoid generalizing an older module to current production. package.json includes web-ifc/ThatOpen dependencies; presence is not validated IFC export functionality. Main website README blob c0c7848fdd42eab5490898671c34d354c759bcc9 was read successfully.

## Discovery and publication target
Accessible account listing returned relevant additional repositories: Engineering-Frontend, steel-verification, Snow-Calculator, wind-calculator, seismic-calculator, WoodDessign, linkoteq-drawing-reconstruction and linkoteq-structural-detection. They are discovery evidence, not reviewed implementation contracts. No gateway was used.

`dehghoon/linkoteq-structural-importer` was not in the listing and direct metadata lookup returned 404. This means not accessible/found in this session, not proof that no private repository exists. No create-repository connector capability was discovered. Proposed temporary additive location: `dehghoon/linkoteq-structural-core`, branch main, `knowledge/importer-initiation/`. This path was absent from the inspected recursive tree and contents read returned 404. No existing root status or other agent handoff will be overwritten.

## Private sample access
The named SBK fixture was found and read through authorized file access; the read returned all available text with no further page. It confirms source syntax observations recorded in the capability matrix. Original byte transfer, hash verification and parser execution were not performed. No source file, customer metadata or source engineering values are included in this public-ready package. The source remains private; synthetic fixtures must replace it in public tests.

## Evidence state
Documents authored: yes. Parser implemented/run: no. Fixture tests/third-party tests: not run. CI: not run. IFC created/validated: no. Deployment/production: not tested. GitHub publication: pending exact-diff review. No separate GPT session was notified.

## Repository creation follow-up — 2026-10-28
User subsequently created dehghoon/linkoteq-structural-importer. GitHub metadata read succeeded: public, default branch main, pull/push permissions reported. Main ref read returned HTTP 409, Git Repository is empty. There is no base commit. This supersedes the earlier 404 and temporary-location proposal; those observations above are historical. Publication target is now repository root. No write has occurred.
