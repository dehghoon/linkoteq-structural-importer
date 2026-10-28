# IFC Mapping Specification

Version 0.1 draft, 2026-10-28. Owner: GPT-1; exporter owner: GPT-3. Target: IFC4, proposed precise schema IFC4 ADD2 TC1. Schema/profile selection is subject to downstream interoperability confirmation. No IFC artifact or conformance test has been produced by this specification.

## 1. Scope and gates

Use IfcOpenShell after dependency/license approval; do not build a STEP serializer. Export validated canonical Core entities with a separate provenance/fidelity manifest. Export is not source-archive replacement and does not prove analysis equivalence. IFC schema expressiveness, implemented exporter coverage and downstream importer support are separate capability dimensions.

Maintain independent profiles: `physical-preview`, `analytical`, and `combined`. No profile currently passes Gate 3. The first prototype may use synthetic, fully specified Core fixtures. Private source models remain access-controlled. Physical geometry is only emitted when actual cross-section/profile and placement are established; analysis properties A/Iy/Iz/J alone cannot reconstruct a unique physical shape.

## 2. Proposed mapping matrix

The table is a design target. Except for structural curve-member axis rules directly reviewed below, exact entity constraints, enum values and relationship signatures must be checked against the pinned IFC4 schema before implementation approval.

| Canonical meaning | IFC candidate | Required controls / exclusions |
|---|---|---|
| Project and units | IfcProject; IfcUnitAssignment; representation contexts | Explicit length, force/mass and derived units; no implicit millimetre/metre choice |
| Established building/storey hierarchy | IfcBuilding; IfcBuildingStorey; spatial relations | Do not infer storeys from every distinct elevation; record generated organizational context separately |
| Physical beam/column/brace | IfcBeam / IfcColumn / IfcMember | Type based on known role; profile, length, placement and offsets required; no guessed I-section |
| Physical wall/slab | IfcWall / IfcSlab | Thickness, boundaries, openings and orientation verified; analytical mesh is not automatically a physical wall |
| Analysis model | IfcStructuralAnalysisModel | Explicit analytical model grouping and coordinate context; independent of spatial physical representation |
| Analysis node | IfcStructuralPointConnection | Preserve stable node identity; coincident nodes not merged |
| Straight analytical member | IfcStructuralCurveMember | Connectivity/topology plus Axis; physical object, if present, has separate identity |
| Analytical surface | IfcStructuralSurfaceMember | Winding, local normal, thickness and connectivity must be validated |
| Material | IfcMaterial and appropriate material associations/properties | Typed units and physical meaning; mass versus weight density unresolved blocks density export |
| Section | IfcProfileDef subtype and material profile association | Emit shape only from verified geometry; section designation/library edition retained |
| Supports and springs | IfcBoundaryNodeCondition and structural connections | Verify stiffness-select representation and all six DOFs; missing is not free/fixed |
| Member-end releases | IfcRelConnectsStructuralMember connection conditions | Must not be applied as global node support; boolean/release convention must be tested |
| Load cases and activities | IfcStructuralLoadCase; structural actions and load resources | Deferred pending exact profile for force/moment frames, units and target relationships |
| Linear combination | Structural load grouping relationships | Deferred until exact grouping/factor semantics verified; no claim that arbitrary Core combinations transfer |
| SRSS/CQC, nonlinear commands, design instructions | Fidelity manifest/source extension | No initial semantic IFC export; optional labeled metadata is not executable equivalence |
| Source identity and provenance | Custom Linkoteq property sets and external document references | No use of reserved standard Pset names for custom schemas; no private access URLs or source bytes |

Properties stored as strings are metadata-only unless an explicit mapped semantic field and validation rule exists. A viewer displaying a source property does not prove an IFC analysis consumer can use it.

## 3. Coordinates and member axes

buildingSMART IFC4 ADD2 TC1 `IfcStructuralCurveMember` defines analytical x along the reference-curve tangent. `Axis` supplies the direction used to establish local z; y completes the right-handed frame. This differs from common physical swept-solid extrusion axes. Preserve Core start-to-end ordering and export Core local z as the appropriate IFC analytical Axis in the declared placement frame, after applying the approved Core-to-IFC rotation. Do not copy the same placement matrix blindly between physical extrusion and analytical curve representations.

For prototype tests use an identity world transform and explicit metre geometry fixture only; these fixtures do not resolve production Core SI/US geometry-unit ambiguity. General transform record includes source and destination frames, length scale, proper rotation, translation, origin choice and inverse. No unapproved axis swaps or georeferencing offsets. Validate endpoints, axis orientation and positive determinants numerically. Degenerate axes, zero-length elements and unresolved section rotation block affected exports.

## 4. Identity, provenance and export result contract

Use a deterministic IFC GUID derivation from a stable project namespace, canonical entity ID and representation role. The same member's physical and analytical entities require distinct GUIDs. Keep the full reverse table: Core ID, source entity/record IDs, IFC GUID, representation role and exporter version. STEP entity numbers are serialization details, not stable IDs. Hash-derived identifiers must be collision-checked.

Return an export artifact reference and digest, schema identifier, export profile/version, Core model digest/version, transform ID, entity mapping, validation evidence and per-feature omissions. Each source record/entity receives `not-requested`, `exported-semantic`, `exported-metadata-only`, `omitted-unsupported`, `omitted-invalid`, or `blocked-dependency`, with reasons and IFC GUIDs where applicable. Do not replace the original import fidelity report; append an export run linked to it.

Custom `Linkoteq_ImportProvenance` may record Core schema version, importer/exporter version, entity ID and nonsecret source record reference. Archive digest disclosure must follow project privacy policy. Exclude client filenames, local filesystem paths and confidential metadata by default from public examples. External archive references must remain authorization-protected and should use stable application identifiers, not expiring signed URLs.

## 5. Failure and partial export policy

Reject export when project units, schema selection or transform cannot be established. Entity-level failure may yield an explicitly partial artifact only if the user-selected profile permits it and the fidelity report identifies every omitted entity and dependency. Never create dummy materials, standard sections, zero loads or guessed supports to satisfy schema validity. No automatic analytical fallback from physical-profile failure without an explicit requested profile.

An analysis-only source can legitimately produce analytical IFC without a physical solid. Conversely, valid physical IFC has no implied load/support/solver coverage. Keep both distinctions in UI and download metadata.

## 6. Validation requirements

1. Parse the emitted IFC with the pinned library. Validate schema types, mandatory attributes, inverse/relationship constraints and available EXPRESS rules. IfcOpenShell validation is one layer, not a complete engineering correctness test.
2. Check unique GUIDs, all references resolving, no orphan analytical members/connections, intended physical/analytical association and correct model membership.
3. Check units and geometry: finite coordinates, expected endpoint distances, cross-section orientation, winding/normal direction, nonzero lengths/areas, physical solid validity where applicable.
4. Verify numeric inverse transform, source/Core/IFC ID coverage, expected counts and exact exported/omitted status counts.
5. Reopen with an independent IFC implementation selected by GPT-3 and record its name/version. A second viewer based on the same IfcOpenShell kernel is not independent implementation evidence. Test analytical access separately from visible physical solids.
6. Maintain artifact hash, fixture hash, expected numerical results, validator versions, complete diagnostics and screenshots where useful. Screenshots alone cannot establish structural correctness.

## 7. Initial fixtures and pass criteria

| Fixture | Expected checks |
|---|---|
| One explicit 3 m horizontal analytical member with two nodes and given local axes | One curve member, two connection identities, length 3 m, correct axis and endpoint order |
| Vertical and skew members with explicit rotated sections | No Y/Z swaps, right-handed frames, stable IDs and correct physical/analytical placement distinction |
| Rectangular section with explicit dimensions plus A/I/J | Solid dimensions match geometry; analysis properties preserved independently |
| Section with analysis properties only | No invented physical solid; analytical-only export or explicit omitted physical body |
| Two coincident nodes with distinct IDs | Identity/topology retained; no unapproved weld |
| Surface with opening and known normal | Boundary/void relationships, area and pressure direction checked when the profile supports them |
| Unknown units, invalid connectivity, missing material | Blocked/partial outcome matches policy; no successful complete-export claim |
| Unsupported SRSS/design instruction | Retained source provenance and omission report; no ordinary linear combination substitute |

Proposed numerical tolerances for synthetic geometry tests: absolute coordinate/length tolerance 1e-9 m with relative 1e-9; orthonormality and determinant residual 1e-10. These are test targets, not engineering equivalence tolerances for arbitrary source precision. Large-coordinate and source-rounding cases need explicit fixture-specific tolerances. Boolean topology, IDs, status accounting and reference resolution are exact.

## 8. Open decisions and evidence

GPT-4 must resolve Core release designation and geometry/density boundary conventions. GPT-3 must pin IfcOpenShell package/schema, establish destination tools/model-view requirements and prove supported relations. GPT-1 must review loads, supports, releases and physical/analytical eccentricity mappings before Gate 3. No IFC4.3 documentation may silently substitute for an IFC4 entity contract.

Primary documentation read:

- IFC4 ADD2 TC1 structural curve member: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifcstructuralanalysisdomain/lexical/ifcstructuralcurvemember.htm
- IFC4 ADD2 TC1 structural example entry: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/annex/annex-e/structural-curve-member.htm (discovered; example execution not performed).
- IfcOpenShell validation API: https://docs.ifcopenshell.org/autoapi/ifcopenshell/validate/index.html (documentation inspected; package/runtime not validated).

Direct retrieval of IFC4 analysis-model, structural-member-connection and boundary-node-condition detail pages returned HTTP 403 in this research session. Their detailed fields therefore remain verification dependencies rather than approved implementation contracts.
