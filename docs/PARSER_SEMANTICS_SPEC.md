# Parser Semantics Specification

Version: 0.1 draft. Date: 2026-10-28. Owner: GPT-1. Implementation target: independent Python engine. Core target: main-declared 0.5, release designation unresolved. This document defines a bounded first implementation, not universal source-format support.

## 1. Evidence and authorization boundaries

Evidence classifications: VERIFIED-DOC means the linked primary documentation was read; OBSERVED-SAMPLE means the private fixture was inspected by the coordinating GPT-1 task; PROPOSED means a normative importer decision requiring tests; BLOCKED means semantics are not authorized for Core mapping. Sample observations do not establish all vendor versions. No private sample bytes, identifiers, or project details belong in public fixtures.

| Profile | Verified evidence | Initial permitted work |
|---|---|---|
| ETABS E2K / .$et | CSI identifies .e2k and .$et text forms; its saving documentation describes corresponding exports as identical | Byte archive, format evidence, record indexing; version-specific semantic grammar requires export fixtures |
| SAP2000 S2K / .$2k | CSI documents text import/export and selected-table/selected-object export | Byte archive and version-aware table inspection; no assumption of complete model |
| STAAD STD | Bentley documents semicolon-separated coordinate/incidence records and scientific numeric notation; private sample shows command blocks | Bounded Cartesian geometry/source-IR parser; rich behavior retained pending semantic rules |
| STAAD SBK | Bentley explicitly documents binary prefixes in some .sbk backups; private sample has recognizable STAAD text | Shared STAAD grammar only for a positively identified payload; preserve prefix and suffix byte ranges |

ETABS binary .EDB, SAP binary .SDB, arbitrary ZIP recovery containers and unrecognized binary data are not text grammars. Store within authorized upload limits; report unsupported decoding. The filename extension is evidence, not authority.

## 2. Decoder, lexer and record ownership

Archive original bytes before decoding. Detect BOM and approved encodings without replacement-character decoding. Unknown encoding produces a diagnostic and leaves the affected bytes uninterpreted. Record original newline sequences, trailing whitespace and byte offsets. UTF-16 byte offsets must not be confused with character offsets.

Every byte belongs to a raw span, including headers, whitespace, comments, unrecognized records and binary prefixes. Logical records contain an ordered list of raw spans, so continuations and multiple records per physical line remain reversible. Line numbers are one-based; byte ranges are zero-based half-open intervals. A logical record identifier is archive-scoped and deterministic. Never regenerate the archive from normalized tokens.

Keyword comparison may be case-insensitive only within a confirmed grammar profile. Preserve identifier spelling, quoting, leading zeros and original numeric lexemes. Do not lowercase entire lines. Numeric parsing is locale-independent: signed decimal and scientific notation; reject nonfinite numeric values for engineering use. Unknown exponent forms, delimiters or abbreviated keywords remain unsupported until verified for the selected dialect.

A semicolon is a record separator only in the active grammar context; it is not a universal command separator. A trailing hyphen is a continuation marker only in a confirmed STAAD continuation context; a negative number is not continuation. Preserve the original segments and limit continuation length and token count. Unterminated strings/continuations generate errors without consuming an unbounded rest-of-file.

## 3. Common parser contract

Input: archive reference, explicit decoder/dialect options, resource-limit profile. Output: source IR, record-span index, syntax diagnostics, feature inventory and format/version evidence. Output is independent of Core mapping success. The same bytes and options produce the same ordered semantic records and diagnostics, excluding operational timestamps/job IDs.

Record fields: record ID, span references, command/table kind, raw tokens, typed fields when parsed, references, state-before/state-after references, parser profile/version, parse outcome and diagnostic IDs. Unknown records retain raw spans and contextual placement. Unknown state-changing commands taint downstream interpretation until a verified reset boundary; do not assume unchanged units, coordinate frame, selection or load case.

Diagnostic minimum: stable code, severity, source spans, entity references, reason, affected capabilities and recovery action. A syntactically parsed record is not automatically semantically understood, Core-mapped, visualized, exported, analysis-supported or equivalence-verified.

## 4. STAAD bounded grammar and state machine

The initial grammar below is a proposed strict subset, supported by observed source syntax. It deliberately excludes vendor shorthand, generated geometry and optional clauses. Tests must distinguish supported-subset parsing from full vendor acceptance.

```ebnf
model_start = "STAAD", "SPACE", [opaque_title] ;
unit_record = "UNIT", length_unit, force_unit ;
joint_header = "JOINT", "COORDINATES" ;
joint_record = positive_integer, number, number, number ;
member_header = "MEMBER", "INCIDENCES" ;
member_record = positive_integer, positive_integer, positive_integer ;
data_line = record, { ";", record }, [";"] ;
number = [sign], decimal, [exponent] ;
```

For the first profile, permit explicit INCHES/KIP and METER/KN unit pairs observed in the fixture. Other spellings require profile-specific tests. Cartesian joint tuples mean source ID and three coordinates in the active source length unit. Member tuples mean source ID, start joint, end joint, with order preserved. Four-or-more-field incidence records, coordinate-generation clauses, CYLINDRICAL, JTORIG, REPEAT, REPEAT ALL, SET Z UP and other coordinate-affecting commands are not accepted as this minimal grammar. They must be preserved and block affected geometry interpretation rather than be partially mistaken for plain tuples. STAAD PLANE and TRUSS are future separately tested profiles, not aliases for SPACE behavior.

State includes section, active units, coordinate convention, selection expression, material/property assignment context, current load case, analysis phase and design context. Initial engineering unit/frame state is unknown until explicit validated evidence resolves it. A new header terminates a recognized data block only when that header is syntactically confirmed; unexpected text remains an unknown record with a resynchronization diagnostic.

References are resolved in a second pass. Forward references may be retained; undefined references block dependent mapping. Duplicate definitions retain every occurrence and raise a conflict; do not choose first/last without vendor-specific validated rules. Coincident coordinates do not authorize node merging. Zero-length member geometry is invalid for frame mapping. No implicit member type, material or section is fabricated.

### Selection expressions and engineering blocks

The private fixture confirms `TO` ranges, `ALL`, lists and trailing-hyphen continuation. Store both source expression and resolved ordered set; selection resolution must record the entity universe and assignment point. Proposed ascending `a TO b` expansion is inclusive, bounded and applicable only in a validated selection context. Descending ranges, BY increments, named groups, negative values or syntax variants are unsupported until tested. Never expand an unbounded range before checking resource limits.

The following tokens/blocks were observed, but are NOT authorization for complete engineering transformation: CANADIAN section tables; ST and LD section forms; SP parameters; pinned supports; START/END MY/MZ releases; material assignment; nodal and member load contexts; UNI GX/GY/GZ; SELFWEIGHT with LIST selection; linear combination blocks; SRSS GENERATE; PERFORM ANALYSIS; CODE CANADIAN; CHECK CODE. Preserve complete records and cross-references. Catalog edition, compound-angle spacing, release meaning, local axes, density and loading signs require dedicated evidence and numerical fixtures.

SRSS GENERATE and any SRSS/ABS/CQC combination are separate source semantics. Negative source case identifiers in a combination cannot be converted into negative Core load-case IDs or ordinary algebraic factors. Do not flatten them into Core `LoadCombination.factors`. Distinguish result combination, repeated loading and nonlinear load application. Analysis and design commands are inert data; never execute them as process or shell instructions.

## 5. ETABS dialect contract

Record source product/version when explicitly present. E2K and .$et share grammar components only after version-specific fixture equivalence. Do not apply SAP tabular parsing merely because both products are CSI. Build a lossless tokenizer before semantic blocks. Preserve section headers, story-relative labels, quoted names, property definitions, assignments, load patterns and analysis cases separately.

No complete E2K token grammar was established from the official pages reviewed. Therefore engineering promotion is blocked until GPT-2 receives a licensed/synthetic export corpus, expected entity counts and exact dictionary of fields. Required first fixtures: one-story portal with explicit dimensions; repeated point/member labels across stories; mixed property assignments; explicit local-axis rotation; one load of each approved primitive; unknown section; older/newer export versions. A successful import into ETABS is useful source-validity evidence, not Linkoteq equivalence proof.

## 6. SAP2000 dialect contract

Separate modern tabular text and legacy V6/V7 profiles: CSI documents different import routes. For modern table-shaped content, a proposed lexer preserves table names, key/value tokens, quotes, continuations and duplicate keys in order. Do not silently coerce a duplicate-key record into a dictionary. Table/column dictionaries and continuation syntax must be validated against pinned SAP exports before semantic mapping.

Model-definition, analysis-result and design-result tables have different capability states. Files can contain selected tables or objects only. Record completeness as `unknown`, `source-declared-complete`, or `known-partial`; no importer may infer whole-model fidelity from a syntactically complete file. Missing materials or sections remain missing references, not default objects. .$2k backup support requires its own completeness warning and dialect fixtures.

## 7. Units and axes contract

Attach active units at the point each numeric token acquires meaning. Retain original magnitude/unit and conversion provenance. Dimension exponents distinguish length, area, second moment, force, force/length, force/area, mass density, weight density, translational stiffness and rotational stiffness. Temperature increments and absolute temperature need separate conversion rules.

Do not assume source Y-up or Z-up equals viewer convention. Record a proper orthonormal source-to-Core rotation R and translation t, with source length scale s: p_core = s R p_source + t. Inverse is p_source = R^T(p_core-t)/s. Forces transform by R after force scaling; moments require force-times-length scaling. No translation is applied to a free force/moment vector; changing its reference point requires a separately specified moment transport operation. Only proper rotations with determinant +1 are in this initial contract.

Member-local +x follows the retained start/end incidence. Supply explicit validated y/z axes for engineering loads/releases; deterministic arbitrary axes are inadequate when source local actions are present. Core geometry boundary units and `rho` mass/weight interpretation require GPT-4 resolution before production mapping. Do not derive G from E and nu without an approved constitutive assumption.

## 8. Acceptance and unresolved items

Required checks: byte recovery; every byte/span accounted for; decoding failures retained; LF/CRLF/CR; semicolon records; continuations; scientific notation; lower-case keywords; unit switches; duplicate and missing references; unsupported state changes; large ranges; catalog misses; SRSS preservation; stable IDs and deterministic output. Each supported transform needs independently specified expected values plus inverse checks; parser round-trip alone is insufficient.

BLOCKED: general E2K/S2K grammars, vendor-version dictionary coverage, STAAD support/release and local-axis transformation approval, hybrid SBK payload classifier validation, source result semantics, source-catalog licensing, and full Core promotion for missing mandatory properties. GPT-2 may implement archive/lexer/source IR and strict STAAD tuple parsing; it may not present these as complete model conversion.

## Sources

- CSI ETABS saving: https://docs.csiamerica.com/help-files/etabs/Menus/File/Saving_Models.htm (VERIFIED-DOC).
- CSI ETABS export: https://docs.csiamerica.com/help-files/etabs/Menus/File/Export/Export.htm (VERIFIED-DOC).
- CSI SAP export and partial-file warning: https://docs.csiamerica.com/help-files/sap/Menus/File/Export/Export_SAP2000_s2k_Text_File.htm (VERIFIED-DOC; page wording includes .$2k, so actual dialect must be fixture-verified).
- CSI SAP legacy importer: https://docs.csiamerica.com/help-files/sap/Menus/File/Import/Import_SAP2000_V6_or_V7_s2k_File.htm (VERIFIED-DOC).
- Bentley SBK recovery: https://bentleysystems.service-now.com/community?id=kb_article&sysparm_article=KB0111473 (VERIFIED-DOC).
- Bentley semicolon records: https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0112643 (VERIFIED-DOC).
- Bentley scientific-coordinate example: https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0113921 (VERIFIED-DOC).
- Private validation fixture: inspection reported by GPT-1 coordinator; access-controlled evidence retained separately. No public redistribution authorization inferred.

## 9. CSI sample-grounded amendment — 0.1.1-draft

This section supersedes statements that no CSI sample corpus has been inspected. Two private byte-identified samples are now reviewed, as recorded in CSI_SAMPLE_COVERAGE_AUDIT.md. They establish observed syntax, not universal grammar or completed semantic conversion. ETABS profile candidate `etabs-text-13.2.2-observed`; SAP profile candidate `sap-tabular-19.0.0-observed`. They are not approved capability claims for other versions. Original models remain private. Parse the complete file before emitting a canonical model.

### 9.1 Lexical and assembly contract
ETABS lexer must recognize quoted strings and bare keywords/numbers as separate tokens even when no whitespace follows a closing quote (observed adjacent RELEASE/CARDINALPT and code/THDESIGN tokens). Do not strip quotes by whitespace splitting. Preserve exact numeric lexemes, punctuation in section labels and keyword case. Repeated MATERIAL, FRAMESECTION, SHELLPROP, FUNCTION, LOADCASE and COMBO statements may contribute fields or ordered child entries to one entity; do not classify every repeated name as a duplicate entity. Keep an ordered record list, field contributions and conflict diagnostics. Repeated mutually exclusive scalar values require a validated vendor precedence rule; until then preserve both and block dependent mapping.
ETABS STARTCOMMENTS to ENDCOMMENTS is an opaque historical text context. Current program/version comes from model program information, not historical save messages. A keyword-looking log line must not change parser state. Preserve terminal END and END OF MODEL FILE separately. If comment termination is missing, preserve the rest and report an incomplete context rather than executing it as model records.
SAP has explicit TABLE headers, key=value records, quoted values and underscore physical continuations. Join logical records only under the confirmed continuation context while retaining each byte span. Do not drop blank tables, unknown columns, repeated keys or explicit empty/zero values. Distinguish table row identity from engineering entity identity: combinations and function series intentionally have multiple rows per name. Unknown fields retain order/value/spans.

### 9.2 Units and two-pass resolution
SAP PROGRAM CONTROL appears after geometry in the reviewed file and states KN, m, C; DATABASE FORMAT TYPES records UnitsCurr=Yes. Pass one inventories global control tables and source-version evidence; pass two resolves dimensions. Do not treat the absence of units near the first geometry record as permission for defaults, or apply the last units to unrelated dialects. Multiple conflicting PROGRAM CONTROL records, per-table overrides or unsupported UnitsCurr settings produce UNITS_UNRESOLVED for dependent values. Exact field-unit dictionaries must be verified before Core promotion. Source dimensions remain tagged with unresolved units when needed.
ETABS UNITS states N, MM, C near the start. Store force/length/temperature roles separately. These are file observations, not approval to infer all obscure property units. Weight-per-volume and mass-per-volume are different dimensions. SAP UnitWeight and UnitMass are separately retained; Core rho selection remains an explicit reviewed mapping. Preserve true zero values (including weightless materials and mass/weight modifiers); a truthiness fallback is prohibited. No conversion by unapproved assumed gravity.

### 9.3 Geometry, scopes and identity
ETABS POINT is a source point/template; POINTASSIGN and LINEASSIGN carry story context. Resolve story-relative objects using scoped identity and a verified story-height/elevation rule. The observed story list is top-down and includes an explicit Base elevation. Do not assign z=0 when a POINT has only x/y, do not interpret HEIGHT as absolute elevation, and do not instantiate every template at every story without assignment semantics. Preserve the trailing LINE connectivity field until its version-specific meaning is verified. It must not be discarded as harmless.
SAP joint IDs and frame IDs are unique in their respective inspected tables, but some joint GUIDs repeat. Use typed, scoped source identifiers for identity; keep GUID as provenance with a collision diagnostic. Never merge different source IDs because their GUIDs or coordinates coincide. SAP coordinate-system rotations and joint local axes must be established before mapping local spring/restraint data; absent definitions are not proof of GLOBAL alignment.
SAP steel overwrite rows repeat some frame identifiers. Preserve all occurrences and compare duplicate values separately from entity lookup; do not overwrite the prior row in a dict. Invalid conflicting repeats block the affected design interpretation, not unrelated byte preservation.

### 9.4 Loads, cases and combination graph
Separate LoadPattern, AnalysisCase and Combination namespaces in source IR, even when names match. Preserve case→pattern edges with scale factors, initial conditions, analysis type and RunCase intent. RunCase=No does not mean discard definition, and presence does not prove execution.
Eligible linear-static cases may eventually emit per-case canonical loads by multiplying approved pattern actions by case factors. Each emitted load must carry provenance to pattern, case and factor; repeated use across cases creates distinct canonical load IDs. The source pattern/case graph stays preserved. Do not perform this lowering until source load units/directions/self-weight semantics are verified; never double-count pattern self-weight or conflate an imported result combination with a load application sequence.
ETABS COMBO may reference LOADCASE or LOADCOMBO. Build a typed dependency graph; check missing refs and cycles. Nested linear-add combinations may only be flattened by an approved algebraic rule with path provenance and summed repeated case coefficients. Envelope/SRSS/CQC/absolute operators must remain operators; no factor-only flattening. Preserve operator-local tags and source combination IDs even if a later canonical derived combination is emitted.
ETABS RDIST/RDSTART/RDEND and SAP DistType/RelDist/AbsDist are explicit station inputs. For a verified relative-distance profile, x=rL. If both relative and absolute values occur, cross-check with a fixture-specific tolerance and retain both; do not silently prefer one on disagreement. Preserve source start/end ordering. GRAV is a vendor direction token requiring its own sign rule; it is not automatically positive global Z. Projected distributed loads require their own length measure and must not reuse actual-member-length rules.

### 9.5 Behavior and section semantics
SAP membrane section/area assignments are distinct from diaphragm constraint definitions and joint assignments. Do not create rigid MPC behavior from a section name. Store declared constraint axis/system/multilevel settings, member joint membership, and surface membrane/shell/drilling/modifier fields separately. Core Diaphragm does not encode all this behavior. No new centroid/centre-of-mass/rotation-centre calculation is authorized by this import specification.
Preserve local spring components, six source DOF names and stiffness units. SAP frame PI/V2I/V3I/TI/M2I/M3I and J-end fields need an explicit local-axis/end mapping; ETABS member RELEASE PINNED must never become a nodal support. Preserve cardinal insertion points, mirrors, transform switches, end offsets, rigid factors and angles; their mechanics must not disappear in a geometry-only approximation.
Nonprismatic definitions preserve segment order, length type/value, start/end section references and stiffness interpolation separately by axis (observed Cubic EI33 versus Linear EI22). Section Designer stores individual shapes with materials, dimensions, centres, rotation, flipped state, order and fiber settings. Aggregate A/I/J alone does not define their full geometry/behavior. Retain temperature loads, thermal coefficients, nonlinear material curves and time-dependent settings; no equivalent forces are invented.
Preserve all definitions, including unreferenced defaults, mesh/output-station preferences, PSD/spectrum/time-history/steady-state/wave settings, code overwrites and UI metadata. Distinguish declared, assigned, requested and executed. Do not advertise modal/wave analysis support merely because a definition table exists.

### 9.6 Promotion boundary
The observations resolve fixture availability and syntax examples, not released Core geometry units, vendor axis conventions, catalog licenses, solver equivalence or IFC relation details. CSI-01 through CSI-13 in the acceptance matrix must become executable tests before feature-specific Gate 2. Full source-byte preservation remains required immediately.
