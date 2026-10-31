# Risk-based engineering validation sampling standard v1

Date: 2026-10-31. Applies to SAP2000, ETABS and STAAD.Pro importer test suites.

## Purpose and scope

This standard selects **independent manual/vendor-reviewed golden samples**, NOT which source records are parsed. Every supported source record must be automatically checked for identity, references, extraction completeness and fidelity classification. Unsupported features are preserved and explicitly reported; SKIP is not PASS. A second parser of the same text is a cross-check, not an independent oracle.

## Source basis

- NIST SP 800-142: equivalence partitions, boundary values and combinatorial interaction coverage: https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-142.pdf
- CSI Analysis Reference Manual: joint/frame local axes, springs, restraints, loading: https://docs.csiamerica.com/manuals/sap2000/CSiRefer.pdf
- Bentley STAAD.Pro User Manual: member orientation, supports, springs, load specifications: https://docs.bentley.com/LiveContent/web/STAAD.Pro%20UserManual-v18/en/STAAD.Pro_User_Manual_en.pdf
- buildingSMART IDS: machine-checkable IFC properties and relationships, **not geometry validation**: https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/

The following counts and scoring rules are **Linkoteq project policy**, not numerical requirements prescribed by NIST or vendors.

## Risk dimensions and mandatory case families

| Domain | Required distinct categories to sample |
| --- | --- |
| Nodes/coordinates | negative/zero/large values; close/duplicate nodes; alternate/local axes; unit changes; high connectivity |
| Frames/columns/braces | inclined/short/zero-length; I/J reversal; local rotation; offsets/eccentricities; releases; tapered sections |
| Materials/sections | custom and missing properties; mass versus weight; modifiers; composite/nonprismatic; mismatched assignments |
| Supports/springs/releases | mixed six-DOF restraint; translational/rotational springs; local/inclined axes; zero/negative/extreme stiffness; asymmetric I/J release |
| Loads/combinations | signed nodal/member/surface loads; concentrated/distributed/trapezoidal; local/global; end locations; self-weight; temperature; nested/modal/SRSS/ABS |
| Areas/shells | irregular polygons; winding/normal; local axes; thin/variable thickness; mesh and frame connectivity |
| Units | changes mid-file; length/area/inertia; force/moment; distributed loads; translational versus rotational stiffness; mass/weight |
| Graph/integrity | duplicate/missing IDs; dangling links; undefined materials/patterns; diaphragms; preserved-only or unsupported records |

Mandatory cases are **never waived by low score**: unit changes, local-axis transforms, invalid/dangling identifiers, sign/direction of loads, non-algebraic combinations (including SRSS), missing source information, and every newly discovered unsupported semantic. If absent from current real fixture, add a synthetic fixture and mark real-world evidence missing.

## Deterministic sample count and selection policy

For each format and domain, form semantic equivalence classes from the applicable categories above, with explicit values at both sides of each relevant numeric boundary. For each **present and supported** class select at least **one** independently reviewed golden sample; for each **high-risk** class select at least **two distinct records** when two exist, otherwise take all available and flag the shortfall. Select at least **one negative test** per domain, plus **one pairwise interaction case** for each feasible pair of high-risk dimensions (e.g. local axis x spring, unit change x distributed load). Pairwise cases may cover multiple classes simultaneously. Do not manufacture absent real examples.

Define:
- `C`: number of present supported classes; `H`: number of high-risk classes with at least two available records; `P`: uncovered feasible high-risk interaction pairs after selecting class representatives; `N`: negative-case count (minimum one per domain).
- Initial minimum **unique** golden sample target is `C + H + P`, minus overlaps from samples that cover multiple classes; implement selection as deterministic greedy set cover ordered by risk, then stable source ID, so the actual count is reported, not guessed.
- There is **no arbitrary maximum** on mandatory high-risk classes or uncovered interactions. If sample volume is high, automate golden checks and request manual review of the selected unique records; do not silently drop coverage.
- Default review budget: up to **12 manually reviewed records per format/domain per fixture** as an initial planning estimate, **not a pass cap**. If mandatory coverage exceeds 12, report extra required count and review in batches. If fewer than 12 suffice, do not pad with random records.
- For numeric boundaries choose below, at, above each meaningful threshold where valid; invalid side becomes a negative test. Thresholds come from source specification and dimensional rules, not arbitrary absolute magnitudes.
- Add a deterministic seed and source hash to the manifest for optional random audit samples, but random selection never replaces mandatory strata.

## Risk priority

Critical: incorrect semantics can alter force paths or lose data (local transforms, signs, releases, units, SRSS, dangling IDs). High: complex/custom/rare or unverified feature. Normal: straightforward class with verified golden precedent. A score may sort within a priority, but cannot downgrade mandatory categories. Structural consequence is **unknown** until model analysis and must not be inferred solely from graph degree.

## Required machine-readable selection report

For each format/fixture/domain: source SHA, total records, applicable classes, counts per class, critical/high/normal flags, selected source IDs, reason codes, golden oracle origin, missing classes, uncovered interactions, target/actual counts, CI evidence URL and statuses PASS/FAIL/PENDING/NOT_IMPLEMENTED. Record automated full-record checks separately from manually reviewed golden coverage. Review on parser, source format, unit or Core contract changes.

## Current implementation status

This is a **documented selection policy**, not an implemented generic scoring/sampling engine. Existing SAP2000 boundary golden test covers four joints and four frames; it does not meet all domain/format coverage criteria yet. ETABS/STAAD equivalents and full automatic selection reports are NOT_IMPLEMENTED. Do not claim the policy is operational until code and CI evidence exist.

## Implementation progress (2026-10-31)

Initial reusable selector implemented at `src/linkoteq_importer/risk_sampling.py`; real SAP2000 boundary adapter/test at `scripts/test_sap2000_risk_sampling.py`; CI workflow updated. The selector deterministically covers each observed class once and observed high-risk classes twice where possible, with deduplication and source-ID tie breaking. This is a **partial implementation**: pairwise interaction coverage, numeric boundary generation, negative-case generation, manifest JSON output, reviewed golden oracle selection, and adapters for geometry/loads/materials/ETABS/STAAD are NOT_IMPLEMENTED. Selection does not prove engineering correctness. CI status must be checked on the workflow run for commit `6f6f1a5` or newer before claiming PASS.
