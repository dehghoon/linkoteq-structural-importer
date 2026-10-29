# SOURCE PRESERVATION SPEC

Version: 0.1.0-draft | 2026-10-28 | Owner: GPT-1 | Engineering review pending

Core target: 0.5 at b1f25a6b735f4e3c586d4d8497298ebd6f656126. This is an inspected main snapshot, NOT a verified release.

## Immutable source archive
For each accepted upload persist original bytes, original filename, declared extension, SHA-256, byte count, media hint, ingestion timestamp, authenticated project/owner, declared encoding, detected encoding with evidence/confidence, detector/profile version, source application/version (or unknown), and retention policy ID. Never normalize line endings/BOM or transcode the original. Unknown binary prefixes remain in archive. Parser output is a derivative and cannot replace the archive. External dependencies are enumerated with resolved/unresolved state and content hashes when supplied; never follow source paths or URLs automatically.

Object keys are server-generated and tenant-scoped, not filenames. No public hash lookup or cross-tenant dedup visibility. Encrypt transit/storage under deployment policy. Reject over-limit uploads before acceptance, reporting not-preserved; preserve fully accepted uploads before parsing. Streaming failures must not label partial objects as complete. Hash and length checked on retrieval. Transactional manifest references only complete objects.

## Record contract and coverage
Byte offsets are zero-based half-open [start,end); decoded line numbers are one-based and accompany byte offsets. Physical spans partition every byte exactly once, including comments, blanks, BOM and opaque prefix. Logical records reference one or more physical spans and retain order; continuation joining is a view, not rewritten source. Child entities may share parent spans; physical coverage counts unique intervals so no inflated coverage.
Each record stores recordId, ordinal, spans, rawRef, kind, contextBefore/contextAfter, activeUnits, sourceIds, references, diagnostics and processing status. Unit-state changes apply to subsequent numeric records under the approved grammar, never retrospectively. Unknown setters taint dependent context. Unrecognized records remain inspectable.

## Stable identities
Caller supplies stable model namespace; repeat of identical bytes/profile must produce identical IDs. Proposed source ID algorithm: SHA-256 over canonical UTF-8 JSON array [namespace, formatProfileFamily, entityKind, sourceIdentifier, scopeIdentifier]. Preserve identifier case/leading zeros unless source profile explicitly defines numeric equivalence; collisions diagnosed. Canonical IDs prefix kind and full digest; display names stored separately. No floating-coordinate or array-position identity. Anonymous records use archive hash + byte spans + record kind and do not promise edit stability. Explicit duplicate/redefinition handling required; do not append random UUIDs to conceal collisions.
One-to-many mappings use parent canonical ID + transformation-rule ID + deterministic child index. Mapping table stores all source IDs and record refs, canonical IDs, transform versions, and inverse availability. Changing namespace/profile semantics is an explicit migration, not silent ID churn.

## Fidelity dimensions
Each stage has state not-attempted/succeeded/partial/blocked/failed/not-applicable, evidence refs and reason codes. Per-record disposition mapped/preserved/unsupported/invalid is a summary only. Mapped does not imply visualized, exported or executable. Parsed does not imply understood. A mapped record can have unsupported fields; report field-level coverage and partial status.
Report fields: schema/version; archive hash; parser/profile/Core pins; totals by unique physical spans, logical records and entities; per-feature stage counts; assumptions; unit/axis transforms; diagnostics; omitted IFC fields; excluded analysis behaviors; validation evidence; execution timestamp separate from deterministic content. Preserve truth: byte coverage 100% may coexist with semantic coverage 0%. Do not aggregate the eight stages into a marketing fidelity percentage.
Analysis eligibility is evaluated over complete requested cases and the connected dependency graph; dropping a stiffness/load/support-affecting command blocks execution. Preview eligibility is separate. Unknown commands cannot automatically be declared harmless.

## Diagnostics
Diagnostic has stable code, severity info/warning/error/fatal, source spans, entity IDs, stage, message, remediation, affected capabilities and evidence. Codes include ARCHIVE_INCOMPLETE, HASH_MISMATCH, PROFILE_AMBIGUOUS, ENCODING_UNRESOLVED, UNKNOWN_COMMAND, CONTEXT_TAINTED, INVALID_RANGE, DUPLICATE_ID, MISSING_REFERENCE, UNITS_UNRESOLVED, DENSITY_KIND_UNKNOWN, AXES_UNVERIFIED, CORE_GAP, IFC_OMISSION, ANALYSIS_BLOCKED, LIMIT_EXCEEDED. No confidential source text in operational logs; authenticated fidelity reports may include bounded excerpts.

## Retention and deletion
GPT-4 must approve numeric retention, geographic storage and legal obligations before launch. Publish retention/deletion to users. Deletion covers source, IR, derived Core, reports, IFC, caches and queued jobs; backup expiry is disclosed and tracked. Audit log retains only authorized minimal metadata. Cancellation cannot bypass cleanup; expired links do not substitute for deletion.

## Acceptance
Exact-byte recovery and SHA-256 equality; full nonoverlapping physical-span coverage; no missing unknown/comment records; deterministic IDs and reports excluding operational timestamps; idempotent retries; malformed source never executed; failure and deletion tests across every derivative. Archive success alone is never a conversion pass.

## CSI provenance and repeated-record rules — amendment 0.1.1-draft

Authoritative model headers and historical comment/log blocks have distinct contexts. A save-history program version, path or command string cannot override current model control records. Preserve private log bytes but redact source filesystem/client details from operational logs and public reports.
For each vendor entity, retain all contributing records, ordered repeated scalar assignments, repeated child records and their conflicts. Build projections from this record ledger rather than replacing raw records with a keyed dictionary. Explicit zero, empty, absent and vendor sentinel values are distinct states. A Program Determined or Default token is not a computed value.
Retain table-level unit metadata and late global-unit declarations independently of record order; provenance must identify the rule used to attach units. A file hash identifies this source snapshot only and is not a project-global entity identity. Duplicated GUIDs do not merge typed source IDs. Logical record counts exclude continuation fragments; table counts, record counts and engineering entity counts are separate report quantities.
Retain case/pattern/combination graphs and physical/analytical/property/assignment relationships. Mark declarations as unreferenced only after all relevant reference classes have been inspected; otherwise use usage-unknown. Unsupported fields on a mapped object remain visible as partial semantics and may block analysis.
