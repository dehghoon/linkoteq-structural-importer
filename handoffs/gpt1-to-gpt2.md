# GPT-1 → GPT-2: Initial importer contract

Version 0.1.0-draft; 2026-10-28. Review status: pending; not engineering certification.

Core 0.5 main snapshot b1f25a6b735f4e3c586d4d8497298ebd6f656126, no release/tag established. Read docs in this package and canonical Core; do not copy the Core contract.

## Scope permitted after this draft is accepted
Immutable accepted-source archive; exact-byte retrieval; physical/logical span ledger; eight-stage fidelity states; deterministic identity; isolated parser interfaces; synthetic fixture scaffolding. STAAD is first-class alongside ETABS/SAP. Implement profiles into source IR; promotion requires source evidence, declared unit/axis rules and passed oracle tests. No arbitrary production parser or solver implementation is requested by this package.

## Required boundary
ImportResult v0.1.0 wraps optional exact StructuralModel v0.5 plus archive/IR/provenance/fidelity refs. Source namespaces and stable IDs belong to caller/project context. Units and every transform must be explicit. Fail incomplete dependencies instead of inventing materials/sections. No direct PyNite calls.

## Review stops
Core release designation, geometry numeric units, density/gravity, source local axes/releases, isotropic G derivation, catalog assemblies, offsets/truss mechanics, SRSS GENERATE, source grammar versions. Preserve these, do not guess. The private SBK was read via authorized file access but is not redistributable by this handoff. Obtain its bytes privately and record hash before running a fixture.

## Tests and evidence
All P/D/G/M/B/L/X/C/I/F/V/S/R/E tests in the acceptance matrix are specified, none executed here. Record exact hashes, counts, numeric expected values and independent oracle. Transform tolerance is specified; solver equivalence tolerance is unapproved. Failure records and unavailable capabilities must remain visible without paid access.

## Next handoff
Create gpt2-to-gpt3.md only after executed evidence exists: parser API version, Core mapping rules/pin, fixture permissions/hashes, tests/CI, dependency SBOM/license notices, limitations and per-capability Gate 2 outcome. GPT-4 receives status through reviewed GitHub publication; this draft does not notify a separate GPT session.

Structural Calculation Engineer Handoff: implement only reviewed deterministic infrastructure; keep unresolved engineering logic blocked.
