# CORE IMPORT GAP ANALYSIS

Version: 0.1.0-draft | 2026-10-28 | Owner: GPT-1 | Engineering review pending

Core target: 0.5 at b1f25a6b735f4e3c586d4d8497298ebd6f656126. This is an inspected main snapshot, NOT a verified release.

## Classification
A direct equivalent mapping; B explicit verified transformation; C source extension; D proposed Core enhancement; E unavailable engineering execution. D/E may coexist with C preservation. All mappings below are design targets, not evidence of implemented compatibility. Existing Core TypeScript is authoritative; source IR lives outside it.

| Feature | Class / canonical target | Required condition or gap |
|---|---|---|
| Nodes | B Node.position | explicit length unit/global transform; no merge |
| Frame connectivity | A Member.startNodeId/endNodeId | both nodes plus section/material exist |
| Beam/column/brace labels | A Member.type | source-supported classification; brace is not automatic truss behavior |
| True truss axial-only element | C/D/E | releases are not automatically equivalent formulation |
| Physical/analytical segmentation | C/D | stable source-parent map; no physical inference from connectivity |
| Plates/slabs/walls | B Surface | boundary/thickness/material subset only; source shell formulation/mesh retained separately |
| Levels/stories | B Level, Node.levelId | resolve story-relative coordinates and repeated IDs first |
| Groups/names | C; permitted metadata subsets | preserve membership and scope; no fake Core group type |
| Grids/openings | B GridLine/Opening | explicit geometry and valid host |
| Offsets/eccentricities/rigid links | C/D/E | no canonical Member offset; moving endpoints alone changes mechanics |
| Local axes/orientation | B Member.localAxes/rotationDeg | preserve source basis; resolve degree/sign/order; no arbitrary fallback |
| Mesh/duplicate nodes | C/B | topology preserved; solver meshing separate; coincidence warning only |
| Material E,G,nu,rho,fy | A/B Material.analysis | units/density kind; all required properties present; no inferred G without approval |
| Strength/design properties | A typed steel/concrete/wood where exact; C otherwise | fy vs Fu/grade/code edition kept distinct |
| Section A,Iy,Iz,J and optional properties | A/B Section.analysis | source principal axes and dimensions verified; J is not polar moment |
| Catalog/designation | A Section.libraryRef plus designation | exact catalog/version match; a name alone supplies no numerical properties |
| Custom/built-up sections | B/C | retain geometry and assembly; no automatic single-angle substitution for double-angle |
| Modifiers/tapered/variable sections | C/D/E | no canonical varying stiffness field; equivalent section requires approved reduction |
| Six-DOF supports | A/B Support.restraints | global DOF equivalence; rotated partial restraints may need coupling |
| Springs | A/B SupportSpring | single-DOF only, stiffness dimension and directional sign verified |
| Coupled springs/nonlinear links | C/D/E | cannot encode full stiffness/hysteresis in single-DOF spring |
| End releases | A/B Member.startRelease/endRelease | local basis, end and boolean meaning verified; partial stiffness is not release |
| Tension/compression-only | A Member flags; E until adapter proof | compatible analysis mode and element formulation |
| Diaphragms | B Diaphragm | level/surface/node topology subset; source constraints more general than type field |
| Prescribed displacement | B EnforcedNodeDisplacement | load-case, units and reference axes; construction-stage history C/E |
| Load patterns/cases | A/B LoadCase/LoadSource | preserve pattern vs case distinction; source category only, never name inference |
| Nodal forces/moments | B NodalLoad | transform source local definitions to global |
| Member point loads | B MemberPointLoad | station origin, direction and eccentricity verified |
| Uniform/trapezoid loads | B MemberDistributedLoad | actual vs projected length and source interval convention verified |
| Plate/surface pressure | B SurfacePressureLoad | source winding and normal sign; general vector surface loading not in this primitive |
| Self-weight | B SelfWeightLoad | global axis/factor and member target semantics; source scope may include surfaces, Core targetMemberIds does not |
| Temperature | C/D/E | case category exists but no temperature load primitive |
| Moving/wind/seismic generators | C/D/E | explicit generated static loads may map separately; generator semantics remain preserved |
| Response spectra/modal/mass sources | C/D/E | LoadCase.analysisType label does not encode spectra/damping/mode participation |
| Linear combinations | A/B LoadCombination | case factors only, confirm additive linear response semantics |
| SRSS/CQC/envelope/absolute/repeat loads | C/D/E | factors map cannot express operators or nonlinear sequence |
| Analysis instructions | B AnalysisRequest subset; C/E otherwise | linear-static/elastic-iterative/p-delta labels insufficient to establish exact vendor equivalence |
| Results | B canonical node/member results only after units/axes/sign proof | imported results not newly solved; provenance/run association required |
| Design/check commands and output requests | C/E | retain code/edition/parameters/member selection; no fabricated DesignCheck pass/fail |

## Conflicts and enhancement proposals
G-01 release designation: main says 0.5, releases and tags enumerate empty. GPT-4 must designate an immutable approved baseline or arrange release.
G-02 geometry units: ProjectInfo.units is SI/US; Node.position and Level.elevation are bare numbers. Require explicit cross-product unit contract; importer private metadata alone cannot establish viewer agreement.
G-03 density: contract calls rho mass/weight density. UnitValue carries units but kind/gravity conventions need review, especially solver self-weight.
G-04 source provenance: Node lacks metadata. Use sidecar many-to-many map, not invented Node fields. Propose canonical provenance capability only through GPT-4.
G-05 combinations: operator/mode/response dependency requires typed future capability; never use tags to simulate SRSS.
G-06 member offsets, true truss formulations, modifiers, partial releases, coupled restraints, mass sources and thermal loading need typed capabilities if approved across products.
G-07 3D package pins Core 49c0973bd15f6f725e251612785e6f55ff4fede4 whereas status declares a7c7103e46bb98035d907624b92ff8c21931f496; reconcile dependency and tests before claiming integration.
G-08 inspected core-scene.ts swaps (x,y,z)→(x,z,y), a determinant −1 display transformation. This is not automatically an engineering defect, nor verified active renderer behavior; GPT-3 must trace active scene code and test winding, rotations and axial-vector moments. Do not reuse display transforms for Core physics.
G-09 Core README says repository does not contain PyNite, while tree contains adapters/pynite; contract explicitly authorizes separate adapter. Clarify documentation; importer keeps adapter boundary.

## Promotion rule
For each profile/feature pin source grammar evidence, rule ID, source units/axes, destination type/field, validation oracle, inverse limitations and owner approval. Map only dependency-closed subsets. A model containing unknown structural commands may be previewable but cannot be silently analyzed. No enhancement in this package modifies the canonical contract.

## CSI-specific gap refinement — amendment 0.1.1-draft

| Gap | Classification | Engineering rule |
|---|---|---|
| Pattern/case dependency graph | C/D; B only for approved linear-static lowering | preserve separate namespaces; canonical emitted loads per case retain pattern/factor provenance; never duplicate self-weight |
| Nested combinations | C/D; B for verified linear-add flattening only | graph cycle/missing-reference check; envelope/SRSS cannot become scalar factors |
| Membrane vs diaphragm constraint | C/D/E beyond exact Core subset | retain constraint axis/local system/membership separately from surface formulation and drilling DOF |
| Nonprismatic segment/interpolation | C/D/E | EI22/EI33 interpolation independently retained; no arbitrary equivalent prismatic section |
| Section Designer assemblies | C/D; B only when geometry/properties verified | multi-material/component/rotation/fiber definitions not inferred from aggregate properties |
| Zero mass/weight modifiers | C/D/E where Core has no modifier | changing material density is not automatically equivalent; declared zeros cannot become defaults |
| Local spring and release DOFs | B or C/D/E when coupling required | establish source local basis; Core global scalar springs cannot represent arbitrary coupling |
| GUID conflicts and repeated metadata | C sidecar provenance | source typed ID identity; no destructive dedup; no Core GUID field invented |
| ETABS story template identity | B pending source geometry rule | scoped instantiated nodes/members; no z=0 or all-story replication |

G-10: general preservation coverage does not authorize these new mappings. Source profiles and acceptance examples are now available, but the Core baseline/units/density issues remain unresolved. Do not modify Core in the importer repository. GPT-4 must coordinate any canonical extensions.
