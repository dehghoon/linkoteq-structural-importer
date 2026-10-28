# IMPORTER ACCEPTANCE TEST MATRIX

Version: 0.1.0-draft | 2026-10-28 | Owner: GPT-1 | Engineering review pending

Core target: 0.5 at b1f25a6b735f4e3c586d4d8497298ebd6f656126. This is an inspected main snapshot, NOT a verified release.

All tests below are specifications, not execution results. Each fixture manifest requires ID, origin/permission, file hash, encoding/newline, vendor/version, profile, expected records/entities, unit states, mapping results, diagnostics, oracle owner and evidence. Public fixtures are synthetic or explicitly licensed; private SBK stays access-controlled. Exact-byte preservation has zero tolerance. Integer IDs/counts/statuses/connectivity must match exactly.

| ID | Fixture / action | Expected assertion |
|---|---|---|
| P01 | arbitrary bytes including BOM, invalid text, NUL, comments, mixed newline | retrieval identical; SHA/length match; preservation independent of parse |
| P02 | continuation and semicolon records | physical spans cover every byte once; logical children trace all spans |
| P03 | unknown command between known records | retained; semantic scope diagnosed; no silent analysis eligibility |
| P04 | worker crash after archive, retry | same immutable source and deterministic IDs; single completed manifest |
| P05 | tenant A requests tenant B archive/report/IFC | authorization denied without metadata leak |
| D01 | renamed .std/.sbk containing same valid text | shared grammar profile; original names preserved |
| D02 | binary-prefixed .sbk; false STAAD substring | preserve all bytes; no unvalidated stripping or accidental text promotion |
| D03 | extension/content disagreement or ambiguous version | diagnostic; no automatic confident format |
| G01 | synthetic STAAD SPACE, UNIT METER KN, nodes 1=(0,0,0),2=(2,0,0), member 10=(1,2) | 2 nodes, 1 source member; L=2m; missing material/section blocks canonical member |
| G02 | next UNIT INCHES KIP, node 3=(10,0,0) | node3=0.254m in normalized IR; earlier node2 remains 2m; Core unit boundary separately gated |
| G03 | node/member TO ranges with continuation, semicolon, mixed keyword case | expanded ordered IDs per grammar; exact selection, limits enforced |
| G04 | reversed endpoints; vertical and near-vertical rotated members | start/end releases and stations preserved; proper right-handed basis |
| G05 | repeated IDs, missing node, zero length, coincident distinct nodes | errors on ambiguous/invalid topology; coincident IDs not merged |
| M01 | known section properties under length-scale s | area factor s², inertia/J factor s⁴; no Iy/Iz swap without axis rule |
| M02 | Canadian W/C/L and built-up LD spacing | exact catalog identity/version; unavailable catalog yields preserved unresolved assignment |
| M03 | missing G/rho; inconsistent dimensional property | no invented property; blocked affected Core entity |
| B01 | fixed/pinned/free, six independent restraints | per-DOF expected arrays verified against official source profile |
| B02 | i/j releases, partial releases, rotated restraint axes | exact eligible booleans; coupled/partial behavior preserved and blocked |
| L01 | 2m beam, linear transverse w1=2,w2=4 kN/m over [0,2] | resultant 6kN; first moment 20/3 kN·m about start |
| L02 | point force/moment; local vs global; projected load | magnitude/station/direction oracle; projected semantics never treated as actual-length by default |
| L03 | negative gravity, targeted self-weight, density mass/weight | preserve target list; no scope expansion; expected force only after density/gravity approval |
| L04 | combination 1.2 caseA+1.6 caseB | exact case IDs/factors; no response verification implied |
| L05 | SRSS GENERATE, CQC, envelope, repeat load | retained operator and raw data; no ordinary Core factors substitution |
| L06 | surface normal reversal and pressure sign | same physical load after approved normal/sign transform |
| X01 | proper rotation Q about z by +90° | (1,0,0)→(0,1,0); F and M transform consistently; inverse recovers |
| X02 | general rotation of restrained local DOFs | reject promotion when boolean global constraints cannot represent coupling |
| C01 | real version-pinned E2K and S2K minimal exports | entities/properties vs vendor source; preserve unknown tables and selection completeness metadata |
| C02 | quotes, embedded spaces, scientific notation, duplicate table records | profile-specific lexical behavior; never global whitespace-split grammar |
| I01 | repeat identical import with same namespace | identical canonical IDs/content/report ordering, excluding operational timestamps |
| I02 | change namespace; edit anonymous record | documented identity behavior; no claim anonymous edit stability |
| F01 | IFC schema + EXPRESS rules + relation checks | zero unwaived errors; every omitted property in report |
| F02 | IFC independent reimport | agreed counts/topology/units/placements within declared tolerance; analytical and physical checks separate |
| V01 | Core→active 3D scene asymmetric geometry/axes | selection maps IDs; no mirrored rotations/load signs; source hidden features inspectable |
| S01 | max bytes/records/range expansion/CPU/memory | deterministic bounded failure and archive outcome; no command execution/network traversal |
| S02 | pathological nesting, enormous TO, malformed number, NaN/Inf | fail within limits; no unbounded allocation, fabricated zero or partial hidden success |
| R01 | cancel/delete/expire source job | derivatives, queued work and access links handled per approved retention policy |
| E01 | independently solved frame/beam/support/release benchmark | only approved adapter; forces, reactions, deflections and signs checked per reviewed tolerance |

## Numeric comparisons
Proposed pure-transform test tolerance: abs(a−b) ≤ max(1e−12 in the explicitly named target unit, 1e−10 max(abs(a),abs(b))). Basis orthogonality/determinant error ≤1e−10 for synthetic fixtures. Source decimal precision and geometric scale require separate engineering acceptance tolerances; do not use this test tolerance as a node-merging threshold. No solver equivalence tolerance is approved yet; GPT-1/reviewer must set benchmark-specific force/displacement tolerances and source solver/version/settings.

## Performance plan
Benchmark 10³, 10⁴, 10⁵ and 10⁶ records within configured admission limits, plus worst-case selections and invalid input. Report machine/OS/parser/dependency pins, wall time, peak RSS, archive/parse/map phase times and throughput. GPT-3/GPT-4 approve budgets before production; no fabricated performance result or SLA.

## Gates
Gate 1 per infrastructure/profile contract; Gate 2 requires executed fixtures/CI at exact commit; Gate 3 requires active viewer and independently inspected IFC; Gate 4 requires security, deployment, URL and representative production import/export. File change, commit, push, CI, deployment creation, health, URL and smoke test remain eight separate evidence entries.
