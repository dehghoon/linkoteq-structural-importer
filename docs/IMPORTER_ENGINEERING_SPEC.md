# IMPORTER ENGINEERING SPEC

Version: 0.1.0-draft | 2026-10-28 | Owner: GPT-1 | Engineering review pending

Core target: 0.5 at b1f25a6b735f4e3c586d4d8497298ebd6f656126. This is an inspected main snapshot, NOT a verified release.

## 1. Document Control
Initial implementable infrastructure specification; vendor semantic promotion remains gated by evidence. No professional certification, parser execution, solver equivalence, IFC conformance or production approval is asserted. Source evidence is in REPOSITORY_INSPECTION.md and the research audit. GPT-4 owns baseline designation and engineering review routing. No Core modification is proposed in this package.

## 2. Calculation Overview
Independent Python importer: archive bytes → detect profile → lossless lexical records → source-specific CSI/STAAD IR → validate semantics → map eligible dependency-closed entities to StructuralModel → downstream 3D/IFC/approved analysis adapter. Archive commits before parser dispatch, independently of parser success. This product is an interoperability service; no new design calculation engine or direct solver call belongs here.
ETABS .e2k/.$et, SAP2000 .s2k, STAAD .std/.sbk are first-class targets. Extensions alone never establish grammar. Other variants require a named versioned profile and fixtures. Analysis/design commands and results remain preserved even when unexecutable.

## 3. Source Inventory
Canonical files: Core contract, TypeScript definitions, update policy, architecture, GPT-1 rules/manual/report guideline, README and PyNite mapping. Integration: 3D package, Core validator/migration, scene mapping, status; website README. Private SBK supplied through authorized file access was read as text; exact original bytes/hash not inspected, parser not executed. No private text is included in this repository package. Official source-format and IFC references are in their dedicated specifications.

## 4. Input Register
| Input | Required / constraint | Default |
|---|---|---|
| source bytes | immutable, size-limited before allocation | none |
| original filename/extension | preserved as metadata, never filesystem path | none |
| project ID, model namespace | authenticated association; stable across retries | none |
| profile hint | optional, must agree with detection | none |
| source version/encoding | record stated vs detected vs unknown | unknown allowed |
| integration units, coordinate transform | approved profile, explicit length/force/mass/time/temperature units | no engineering default |
| limits policy | versioned bytes/records/range expansion/CPU/memory/time limits | deployment must supply |
| assumption approvals | IDs, reason, reviewer, scope and version | empty |
No missing property is filled with nominal steel, generic section, fixed support, inferred dead load or arbitrary gravity.

## 5. Constants and Code Parameters
Conversion constants must have pinned authoritative sources and dimension tests before promotion. No design-code coefficients are implemented. Source code names and editions are retained separately; CANADIAN alone does not establish a CSA edition. Catalog selections require an exact catalog/version/record and matching source dimensions.

## 6. Variable Dictionary
B: original byte sequence; H: SHA-256(B); r: source record; u(r): active unit state; Q: proper orthogonal source-global→Core-global matrix; t: translation; sL: length scale; R: local basis with columns x,y,z; L: member length; c: capability status. Unknown is distinct from false/zero. IR contains vendor semantics; only canonical records cross the engineering boundary.

## 7. Calculation Workflow
1. Enforce authorization and ingress limits; durably archive accepted bytes and hash.
2. Detect encoding/profile without executing file commands. Ambiguity ends at preservation with diagnostics.
3. Partition full byte stream into ordered spans; tokenize without deleting unknown text.
4. Build source IR with unit/context snapshots and original IDs; resolve references after declarations.
5. Validate topology, properties, assignments, coordinate definitions and dependency closure.
6. Apply only approved transforms with trace IDs; record blocked components.
7. Validate exact pinned Core boundary and emit eligible model plus separate source package/fidelity report.
8. Let downstream consumers add their own visualization/IFC/analysis evidence; importer never asserts these on their behalf.
9. Publish job result atomically. Crash/retry must recover original archive without duplicate semantic identities.

## 8. Formula Register
| ID | Rule | Preconditions / verification |
|---|---|---|
| U-01 | q_target = q_source × product(s_i ** dimensional_exponent_i) | known dimension and exact unit definition; independent oracle |
| X-01 | p_core = sL Q p_source + t | QᵀQ=I, det Q=+1; inverse p_source=Qᵀ(p_core−t)/sL |
| X-02 | F_core=sF Q F_source; M_core=sF sL Q M_source | same physical reference point; offsets require r×F moment separately |
| X-03 | x=(p_end−p_start)/L; R=[x y z]; z=x×y | L>0, normalized independent orientation; no guessed source y/z |
| X-04 | v_new_local=R_newᵀ Q R_source v_source_local | proper rotations, appropriate dimension scale |
| L-01 | resultant trapezoid = (w1+w2)(x2−x1)/2 | linear load, same axis, 0≤x1<x2≤L |
| L-02 | linear combination action = Σ factor_i × action_i | linear additive combination only; excludes SRSS/envelopes/repeat-load nonlinear semantics |
These are mathematical transformation requirements, not validated vendor profiles. General rotation of partial restraints or releases may produce coupled DOFs not expressible by Core booleans; reject that promotion. Never transform only force vectors while leaving restraints/sections unchanged.

## 9. Decision Logic
Archive failure: fail ingestion; never claim preservation. Unsupported encoding/profile: preserve and report. Invalid record: retain span and error. Unknown command: retain, mark potential semantic impact, block affected dependency graph. Unknown context-setting command conservatively blocks subsequent dependent records until a validated context boundary. Do not merge coincident nodes. Duplicate identifier with conflicting definition blocks affected entities; versioned reassignment semantics must be explicit. Partial model is visibly partial and excluded from analysis by default. No successful syntax parse implies engineering equivalence.

## 10. Output Register
ImportResult version 0.1.0 contains jobId, sourceArchiveRef, sourceHash, profile/version, parser/version, coreSchemaVersion, coreCommit, status (preserved-only/partial/mapped/failed), optional canonical StructuralModel, sourceIRRef, idMapRef, fidelityReportRef, diagnostics, blockedCapabilities, transformManifest and assumptions. These are transport/source-package fields, not replacement Core types. Source archives and private metadata require authorization on every read. Core model absent if no valid subset exists.
Fidelity report shows eight independent stages: preserved, parsed, understood, Core-mapped, visualized, IFC-exported, analysis-supported, equivalence-verified. Essential errors/limitations remain accessible regardless of payment; downloadable commercial reports are a separate entitlement decision.

## 11. Code Reference Register
Core v0.5 is an integration contract, not a design standard. No engineering code clause has been validated for design execution. IFC schema/version and vendor manual sources belong to their own registers. Private source design-code strings are source-stated only.

## 12. Assumptions Register
A-01: independent importer repository was created by the user and verified empty on 2026-10-28. A-02: publish at the importer repository root; the prior temporary Core documentation location is superseded. No Core schema change. A-03: SI numeric geometry interpretation remains unapproved pending explicit boundary agreement. A-04: no source file completeness assumed; source selection/export settings may omit model information before ingestion. A-05: user-provided sample may be examined privately, not published.

## 13. Validation Cases
See IMPORTER_ACCEPTANCE_TEST_MATRIX.md. All listed implementation tests are required, not run. Document QA does not satisfy Gate 2. No vendor equivalence claim without independent reference output and reviewer approval.

## 14. Issues and Uncertainties
Release/tag designation; actual viewer dependency drift; geometry units and elevation convention; density kind/gravity; source version grammars; built-up Canadian profiles; isotropic G derivation approval; SRSS GENERATE semantics; offset/rigid/truss semantics; IFC exchange view; retention and workload limits; dependency legal review. Owners and stop conditions are in project-status.json.

## 15. Handoff Package for Structural Calculation Engineer
GPT-2 may implement only source archival, spans, diagnostics, deterministic identity and test scaffolding against this initial contract. Grammar prototypes may remain inside source IR. Engineering promotion is permitted per capability only after profile, numerical oracle and Core baseline review. GPT-3 may prepare job/UI/report scaffolding with mocks and IFC research. Neither is authorized to declare production readiness. See ../handoffs/gpt1-to-gpt2.md.
