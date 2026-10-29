# SOURCE FORMAT CAPABILITY MATRIX

Version: 0.1.0-draft | 2026-10-28 | Owner: GPT-1 | Engineering review pending

Core target: 0.5 at b1f25a6b735f4e3c586d4d8497298ebd6f656126. This is an inspected main snapshot, NOT a verified release.

## Evidence and support meanings
P0 preservation is mandatory for every accepted file; P1 source IR decoding; P2 reviewed Core promotion; P3 verified viewer/IFC; P4 independent analysis equivalence. No P1–P4 is marked implemented in this package. A source feature inventory is not a claim every vendor/version supports each feature. Version-specific availability must be verified against exports/manuals. Baseline formats: ETABS .e2k/.$et; SAP2000 .s2k; STAAD .std/.sbk with content detection. Shared grammar only for validated matching syntax.

| Category | Feature requiring inventory | ETABS target | SAP2000 target | STAAD target |
|---|---|---|---|---|
| Geometry | nodes and coordinates | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | frame/beam members | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | truss/brace behavior | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | plates/shells/walls/slabs | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | connectivity | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | physical versus analytical identity | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | offsets/eccentricities | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | local axes | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | groups/stories/levels/names | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | mesh/segmentation | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Geometry | duplicates | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | material identity | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | E | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | G | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | nu | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | density kind | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | strength | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | standard catalogs | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | custom/built-up sections | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | section orientation | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | modifiers | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | tapered/variable sections | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | assignments | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Properties | vendor designations | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | supports | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | elastic supports/springs | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | end releases | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | tension/compression-only | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | nonlinear links | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | diaphragms/constraints | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | rigid offsets | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | prescribed displacement | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Boundary | other vendor conditions | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | patterns/cases | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | nodal forces/moments | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | member point | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | distributed/trapezoid | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | plate/surface | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | self-weight | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | temperature | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | imposed displacement | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | moving loads | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | wind/seismic definitions | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | response spectra/modal | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | linear/nonlinear | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | P-Delta | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | combinations/envelopes | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | SRSS | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Loading | vendor analysis settings | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Design | codes | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Design | parameters | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Design | design groups | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Design | check commands | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Design | available results | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Design | output requests | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |
| Design | report metadata | preserve; semantics pending profile | preserve; semantics pending profile | preserve; semantics pending profile |

## Observed private sample coverage
Private SBK text confirms: 3D header; semicolon coordinate/connectivity records; member/floor grouping; empty user table block; isotropic materials; Canadian standard and built-up section assignments; ALL material assignment; PINNED supports; mixed INCHES KIP/METER KN; TO selections; trailing-hyphen continuation; START/END MY/MZ release commands; seven numbered load definitions; UNI GX/GY/GZ; selected-member self-weight; a linear combination plus two SRSS GENERATE combinations; analysis and Canadian check-code commands. This is manual text inspection, not an executed parser or source-software validity check. Archive bytes, exact hash, counts and numeric oracle remain fixture work. Source metadata and engineering values are intentionally not republished.

Material G is not explicitly supplied in the reviewed material declarations; E/nu-based derivation requires an approved isotropic rule. A declared rigid material is incomplete; unused invalid declarations must still appear in fidelity diagnostics. Canadian TABLE LD and spacing must remain assembly semantics, not reduced to TABLE ST. LOADTYPE None with a seismic-looking name does not authorize automatic seismic category inference. SRSS GENERATE negative case identifiers/trailing sign require Bentley-specific semantic verification.

## Minimum capability progression
Start P0 for all three families concurrently. Build STAAD lexical context/geometry first using approved synthetic fixtures, but preserve assignment and command blocks immediately. Build CSI version-specific tables/blocks in parallel only after authentic licensed examples identify their grammar. P2 geometry cannot invent required Member material/section references. Partial nodes may map with member blocks diagnosed; source-only connectivity is inspectable until required properties resolve. Product claims must name source version and feature subset.

## CSI observed profiles — amendment 0.1.1-draft

Both full source byte streams were inspected; hashes and complete section/table inventories are in CSI_SAMPLE_COVERAGE_AUDIT.md. No runtime importer capability is claimed.

| Feature | ETABS 13.2.2 .$et observation | SAP2000 19.0.0 .$2k observation | Target and gate |
|---|---|---|---|
| Header/units | early N/MM/C, historical versions inside log | late PROGRAM CONTROL KN/m/C; UnitsCurr=Yes | P1 two-pass/opaque-context tests; P2 field unit dictionaries |
| Geometry | 2 point definitions, 1 line, story-scoped assignments | 388 joints, 609 frames, 2 areas | P1 inventories; P2 story/global axes verified |
| Identity | scoped labels; repeated entity definition records | duplicate GUID groups and repeated overwrite rows | typed scoped IDs; preserve every contribution |
| Loads | 4 line loads: POINTF/TRAPF, GRAV, relative stations | 1810 distributed and 579 temperature rows | static subset only after sign/unit/station proof; thermal C/D/E |
| Cases/combinations | 18 patterns; 50 combo declarations incl. envelope and nested refs | 10 patterns, 11 cases, 48 combo names across 244 rows | preserve graph, operators, multiplicity and execution intent |
| Diaphragm/surfaces | diaphragm/property definitions; assignment evidence separate | 151 joint constraints plus membrane areas | preserve separately; no automatic MPC from surface name |
| Boundary | member PINNED plus separate point restraints | 180 release, 55 restraint and 55 spring rows | source local DOFs/end conventions before P2 |
| Sections/offsets | custom sections/cardinal point/modifiers | nonprismatic, Section Designer, insertion/offset and rotation records | C/D/E for mechanics absent in Core |
| Metadata/design | historical log, material curves and design preferences | code overwrites, dynamic functions, mesh/UI/default definitions | P0/P1 preservation; no claim of executed design or analysis |

Counts are source inventory observations, not counts of successfully converted or validated engineering entities. The representative corpus now contains private STAAD, ETABS and SAP examples. Version coverage remains narrow; original files are not public test assets.
