# Initial implementation contract — infrastructure slice

Version 0.1.1-draft, 2026-10-28. Owner GPT-1; implementation owner GPT-2. This document makes the source-preservation slice implementable independently of unresolved vendor semantics and Core promotion. It does not approve structural analysis or a vendor conversion profile.

## Entry and exit
Input: immutable byte stream, display filename, authenticated project reference, stable model namespace, explicit limits policy. Output: ImportResult v0.1.0, archive manifest, ordered physical spans, diagnostics and fidelity report. For this slice coreModel is absent and parsed/understood/mapped/visualized/exported/analysis/equivalence are not-attempted. Archive preservation may succeed independently. No dependency on a geometry unit convention is needed to preserve bytes.

## Required interface decisions
- Archive manifest version 0.1.0: sourceHash is lowercase SHA-256 of exact bytes; byteLength nonnegative integer; originalFilename opaque display text; declaredExtension preserves exact spelling; detectedFormat initially unknown; declared/detected encoding separate nullable fields; sourceApplication/sourceVersion nullable; policyId and project association required. Storage location is opaque, authorized and never derived directly from originalFilename.
- Every fully admitted source is committed before parsing. Above-limit input is rejected with no claim of full preservation. An exact limit L accepts L bytes and rejects L+1. Failed streaming objects are incomplete and never exposed as an archived source.
- Physical span ledger version 0.1.0: each entry has ordinal, startByte, endByte, kind and optional decodedLine. Entries cover [0,byteLength) once in order, with positive width. Empty file has zero spans. An uninterpreted source may be one opaque span. It is valid preservation, not a parse.
- Refined spans replace a ledger revision transactionally; preserve previous revision and source hash. Logical records refer to a ledger version and ordered span IDs; no dangling references after refinement. Byte boundaries never split an encoded character in a decoded span; opaque spans remain byte-oriented.
- Stages use the enum not-attempted/succeeded/partial/blocked/failed/not-applicable. Only preserved may be succeeded in this slice. Unknown format is not invalid source syntax. Never set unsupported merely because parsing has not been attempted.
- Deterministic result payload excludes generatedAt, job ID, signed URLs and transient storage locations from content comparisons. Counts separate bytes, spans, logical records and semantic entities. Opaque bytes do not count as parsed records.

## Identity decision
For known source entities later: serialize [namespace, formatProfileFamily, entityKind, sourceIdentifier, scopeIdentifier] as JSON UTF-8 without BOM, ensure_ascii=false, separators comma/colon without whitespace; all five values are strings; no Unicode normalization, case folding or numeric coercion. ID is entityKind + ':' + full lowercase SHA-256 of those bytes. Entity kind is an approved ASCII registry token. Scope is an explicit string (empty only for truly unscoped identities). Hash collisions with different preimages are fatal. Changing identity algorithm is a versioned migration.
For raw spans use sourceHash + ':' + startByte + ':' + endByte as archive-local identity, with canonical base-10 integers. It is not a stable engineering entity ID and is not promised stable across file edits. Source ordering, material or coordinates never silently determine canonical entity identity.

## Diagnostics and failure contract
Stable codes from SOURCE_PRESERVATION_SPEC apply. Archive write failure returns failed and ARCHIVE_INCOMPLETE; report preserved=failed. Successful archive with unknown decoder returns preserved-only, preserved=succeeded, parsing=not-attempted, ENCODING_UNRESOLVED if decoding was requested. Integrity mismatch blocks retrieval and dependent work, emits HASH_MISMATCH, and never overwrites a known-good archive with suspect bytes. No source text in operational logs. Authoritative diagnostic detail remains available through authorized reports.

## Resource and security boundary
Limits are caller-supplied required positive integers: maxBytes, maxPhysicalSpans, maxLogicalRecords, maxContinuationBytes, maxExpandedSelection, maxCpuMillis, maxWallMillis, maxResidentBytes. Zero/missing/nonfinite limits are configuration errors, not unlimited operation. Values for production need GPT-3/GPT-4 workload approval; test fixtures supply explicit low limits. No parser eval, shell execution, import of source code, path following or external URL fetch. Retention/deletion is policy-governed, not an arbitrary engine constant.

## Synthetic acceptance data
fixtures/preservation/opaque-command.txt is an original synthetic file containing an intentionally unrecognized command. fixtures/preservation/manifest.json specifies exact hash/byte count, a valid one-span opaque ledger and expected stage outcomes. This is a storage/ledger oracle, not valid STAAD input. GPT-2 must also generate in-memory zero-byte, arbitrary binary, invalid UTF-8, BOM, CR/LF/CRLF and L/L+1 limit tests; original bytes must recover exactly. Never advertise fixture generation as a passing parser test.

## Implementation tickets and completion evidence
| Ticket | Work | Required evidence |
|---|---|---|
| INF-01 | Streaming archive and immutable manifest | exact byte recovery, digest, atomic completion, injected write failure |
| INF-02 | Opaque spans and versioned refinements | coverage with no overlap/gap, empty input, invalid span rejection |
| INF-03 | Identity and deterministic serialization | repeated inputs identical, scope/kind separation, Unicode and leading-zero cases |
| INF-04 | Eight-stage report and diagnostics | preservation-only cannot become mapped/analyzed; correct unknown vs invalid |
| INF-05 | Isolation, limits and cancellation | L/L+1, bounded span allocation, failure cleanup, restart/idempotency |
| INF-06 | Contract handoff | pinned implementation commit, runtime/dependencies, tests/CI, exact fixture hashes, limitations |

GPT-2 may begin this infrastructure slice under the project directive. The document is an engineering specification, not evidence that implementation has begun. Vendor numeric interpretation, Core model publication and IFC/solver behavior remain gated. No phantom GPT-2 completion handoff may be created.
