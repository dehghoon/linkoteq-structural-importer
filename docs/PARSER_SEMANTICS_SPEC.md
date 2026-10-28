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
