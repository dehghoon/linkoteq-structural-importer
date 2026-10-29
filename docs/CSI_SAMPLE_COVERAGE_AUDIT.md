# CSI sample coverage audit and required specification addendum

Date: 2026-10-28 (America/Toronto). Owner GPT-1. Compared against importer main commit 66675d5158000aaca4ffe80f2efc08504d2bdd44. Verdict: preservation and feature categories are covered broadly; version-specific executable semantics are NOT complete. Do not mark either sample converted, equivalent or solver-ready. This audit is incorporated into the combined CSI amendment draft; earlier seven-file review is superseded. No GitHub mutation performed.

## Method and privacy
Read both complete local byte streams, calculated SHA-256, inventoried every section/table, inspected representative records and important contexts, and performed limited lexical counts/reference checks. UTF-8 decoding succeeds, but ASCII-compatible bytes alone do not prove the original declared encoding. Both files use CRLF. SAP physical continuation handling and key/value extraction were one-off audit operations, not an authoritative parser. Numeric source-software validation and conversion tests have not run. Original files, local paths, client details and GUID values are excluded from public-ready findings; keep originals private.

## Source identity
- `MTDENN~1.$2k`: 1,654,573 bytes; 12,437 lines; SHA-256 `8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79`.
- `STRUCTURE.$et`: 280,648 bytes; 2,482 lines; SHA-256 `0d6da147686f109ee3fe6c69bf7294a4ed237a17013c6715deb27709161bb21d`.

ETABS declares ETABS 2013 version 13.2.2 and N/MM/C at lines 4 and 7. SAP declares SAP2000 19.0.0 and KN/m/C at line 12357. These are file-stated versions, not installed applications verified in this session.

## Coverage against existing package
Existing sources: PARSER_SEMANTICS_SPEC sections 2, 5–8; CORE_IMPORT_GAP_ANALYSIS mapping table and G-01–G-09; SOURCE_PRESERVATION_SPEC; acceptance cases C01/C02, G04/G05, L02/L05 and I01. Existing text explicitly blocks full CSI grammar pending fixtures, so supplying these samples advances evidence but does not automatically pass that gate.

| Observed requirement | Existing coverage | Required explicit addition / acceptance |
|---|---|---|
| ETABS .$et and SAP .$2k version profiles | named in parser spec, not validated | fixture identities and exact versions; extension alone not acceptance |
| SAP unit declaration after geometry | general units rule insufficient | two-pass discovery of file-level PROGRAM CONTROL before interpreting numeric tables; do not apply STAAD sequential UNIT semantics to SAP |
| ETABS point x/y plus story assignments | story-relative warning only | preserve POINT templates and scoped POINTASSIGN/LINEASSIGN; derive z from verified story elevation/height rules, never missing z=0 |
| ETABS quoted token immediately adjacent to next keyword | quoted names generally mentioned | lexer test for closing quote followed immediately by keyword; whitespace split alone fails |
| Repeated property/case records | generic duplicate warning | distinguish intended multi-record entity accumulation from duplicate whole entity; preserve all records |
| ETABS STARTCOMMENTS/ENDCOMMENTS history | raw comments covered | bounded opaque context; historical version strings/commands cannot override current model; terminal END distinct from log |
| SAP underscore continuations | proposed, unverified | 2395 physical lines end in continuation marker; preserve ordered spans, quote context, malformed continuation failures |
| SAP duplicated GUIDs | stable source identity general | GUID cannot be sole entity identity; 7 duplicate-GUID groups in joint table despite 388 unique Joint IDs; preserve source GUID and diagnose |
| SAP repeated design overwrite keys | duplicate records general | 1106 rows for 605 frame IDs; 501 repeated-ID groups; compare duplicates/conflicts, never silently last-write-wins |
| Load pattern vs analysis case | distinction present | preserve case→pattern factor graph and initial conditions; ETABS one case references multiple patterns; no accidental name-based conflation |
| Nested combination and envelope | envelopes preserved broadly | ETABS LOADCOMBO references require graph, cycle checks and operator semantics; no flattening envelope into additive factors |
| Relative/absolute stations, gravity loads | general transform requirements | ETABS RDIST/RDSTART/RDEND and GRAV, SAP DistType/RelDist/AbsDist must have separate validated rules and consistency checks |
| Mass and weight densities | Core gap already recorded | SAP UnitWeight and UnitMass are separate values; ETABS WEIGHTPERVOLUME is not mass density; preserve zero density and zero modifiers |
| Diaphragm vs membrane surface | generic diaphragm/surface coverage | SAP constraint table + 151 joint assignments is separate from membrane area section; section name does not establish rigid MPC equivalence |
| Springs and releases | general six-DOF coverage | SAP local spring basis and P/V2/V3/T/M2/M3 per-end releases require explicit vendor→Core axes; ETABS PINNED string is member release, not node support |
| Insertion points, offsets and local angles | Core gaps explicit | keep cardinal points/mirroring/transform flags, rigid factors and source angles; no endpoint-only shortcut |
| Temperature loading | C/D/E already explicit | 579 SAP temperature rows must be in fidelity and analysis exclusions, never silently dropped |
| Nonprismatic and Section Designer | variable/custom sections broad | preserve EI33 Cubic vs EI22 Linear and segment length; multi-shape section geometry, rotation, flip and material associations remain distinct |
| Design/mesh/dynamic settings | generic preserve requirement | add exact table inventory including edge constraints, mesh policies, time-dependent properties, PSD/history/spectrum, wave settings, code overwrites and UI metadata |

## Concrete observations and bounded checks
ETABS: two POINT definitions, one LINE definition, two POINTASSIGN and one LINEASSIGN in the visible model definition, 18 load-pattern definitions, four LINELOAD records, and 50 combination declarations (49 Linear Add, one Envelope). Multiple property catalog definitions do not imply instantiated members/surfaces. Story list includes six entries including Base; do not replicate every point at every story. The small object model and lengthy save history do not prove the intended original project was fully exported.

SAP: 72 tables; 388 joint records with unique Joint IDs; 609 frame-connectivity records with unique Frame IDs; 2 area-connectivity records; 1810 distributed-load records; 579 temperature-load records; 180 frame-release records; 96 typical local-axis assignments; 55 restraint records; 55 uncoupled spring records; 151 joint-constraint assignments; 11 load cases; 10 load patterns; 244 combination rows for 48 combination names. Multirow combination records are not duplicate entities. All 609 frame endpoints resolve to the inventoried joint IDs in this limited check. All 1106 steel overwrite records target inventoried frame IDs. These checks do not validate other references, element mechanics, stability or numerical equivalence.

## Required new acceptance cases
- CSI-01: these exact private fixture hashes/versions reproduce section/table inventories; originals never become public fixtures without permission.
- CSI-02: ETABS scoped points/story heights; missing explicit z must not be fabricated; explicit negative base elevation retained.
- CSI-03: ETABS adjacent quoted value/keyword, multiple entity-definition records, empty sections and opaque history context.
- CSI-04: SAP late PROGRAM CONTROL resolves units before numeric interpretation; undeclared/contradictory unit metadata blocks promotion.
- CSI-05: 2395 SAP continuations accounted for with original byte provenance; no line dropped.
- CSI-06: duplicate GUIDs retain distinct source entity IDs; duplicate overwrite records preserved and conflict classification explicit.
- CSI-07: cases and patterns with same names remain separate namespaces; many-pattern case semantics preserved.
- CSI-08: nested combination dependency graph, reference resolution/cycle negative fixture, envelope blocked from linear-factor mapping.
- CSI-09: GRAV/local/global loading and relative/absolute stations checked against independent vendor oracles; no assumed sign.
- CSI-10: zero weight/mass/modifiers preserved; UnitMass vs UnitWeight distinct; units/density Core decision remains required.
- CSI-11: diaphragm constraint versus membrane area, local rotational springs and member releases not conflated.
- CSI-12: temperature/nonprismatic/custom sections/offsets fully retained; unsupported mechanics prevent claiming analysis-equivalent conversion.
- CSI-13: unused/default definitions and present settings distinguished from active/referenced behavior. Presence of a spectrum or wave definition is not proof a corresponding analysis was run.

## Package changes incorporated in this amendment
The combined amendment adds these profile rules and cases to PARSER_SEMANTICS_SPEC and IMPORTER_ACCEPTANCE_TEST_MATRIX, updates SOURCE_FORMAT_CAPABILITY_MATRIX and CORE_IMPORT_GAP_ANALYSIS, extends preservation rules, and links this audit from handoffs and status. These are specification changes; passing implementation evidence is still required.

## Overall finding
YES: both source families and preservation of their engineering categories are in scope. NO: the published package does not yet contain enough version-specific rules to implement faithful conversion of these two examples without decisions. The correct next state is sample-reviewed / specification amendments required, not full conversion approved.

## Complete source section/table inventory
Line ranges identify supplied private files; counts include all physical lines within each block, not semantic entity counts.

### MTDENN~1.$2k

| Section/table | Lines |
|---|---|
| "ACTIVE DEGREES OF FREEDOM" | 3–5 |
| "ANALYSIS OPTIONS" | 6–8 |
| "AREA AUTO MESH ASSIGNMENTS" | 9–12 |
| "AREA EDGE CONSTRAINT ASSIGNMENTS" | 13–16 |
| "AREA SECTION ASSIGNMENTS" | 17–20 |
| "AREA SECTION PROPERTIES" | 21–24 |
| "AREA SECTION PROPERTY DESIGN PARAMETERS" | 25–27 |
| "AREA SECTION PROPERTY - TIME DEPENDENT" | 28–30 |
| "AUTO COMBINATION OPTION DATA 01 - GENERAL" | 31–33 |
| "AUTO WAVE 3 - WAVE CHARACTERISTICS - GENERAL" | 34–36 |
| "CASE - MODAL 1 - GENERAL" | 37–39 |
| "CASE - STATIC 1 - LOAD ASSIGNMENTS" | 40–51 |
| "COMBINATION DEFINITIONS" | 52–297 |
| "CONNECTIVITY - AREA" | 298–301 |
| "CONNECTIVITY - FRAME" | 302–912 |
| "CONSTRAINT DEFINITIONS - DIAPHRAGM" | 913–915 |
| "COORDINATE SYSTEMS" | 916–918 |
| "DATABASE DOCUMENTATION" | 919–920 |
| "DATABASE FORMAT TYPES" | 921–923 |
| "FRAME AUTO MESH ASSIGNMENTS" | 924–1534 |
| "FRAME DESIGN PROCEDURES" | 1535–2145 |
| "FRAME INSERTION POINT ASSIGNMENTS" | 2146–2756 |
| "FRAME LOADS - DISTRIBUTED" | 2757–4568 |
| "FRAME LOADS - TEMPERATURE" | 4569–5149 |
| "FRAME LOAD TRANSFER OPTIONS" | 5150–5760 |
| "FRAME LOCAL AXES ASSIGNMENTS 1 - TYPICAL" | 5761–5858 |
| "FRAME OFFSET ALONG LENGTH ASSIGNMENTS" | 5859–6469 |
| "FRAME OUTPUT STATION ASSIGNMENTS" | 6470–7080 |
| "FRAME RELEASE ASSIGNMENTS 1 - GENERAL" | 7081–7262 |
| "FRAME SECTION ASSIGNMENTS" | 7263–7873 |
| "FRAME SECTION PROPERTIES 01 - GENERAL" | 7874–8125 |
| "FRAME SECTION PROPERTIES 05 - NONPRISMATIC" | 8126–8128 |
| "FRAME SECTION PROPERTIES 13 - TIME DEPENDENT" | 8129–8213 |
| "FUNCTION - PLOT FUNCTIONS" | 8214–8216 |
| "FUNCTION - POWER SPECTRAL DENSITY - USER" | 8217–8220 |
| "FUNCTION - RESPONSE SPECTRUM - USER" | 8221–8224 |
| "FUNCTION - STEADY STATE - USER" | 8225–8228 |
| "FUNCTION - TIME HISTORY - USER" | 8229–8235 |
| "GRID LINES" | 8236–8268 |
| "GROUPS 1 - DEFINITIONS" | 8269–8271 |
| "JOINT CONSTRAINT ASSIGNMENTS" | 8272–8424 |
| "JOINT COORDINATES" | 8425–8814 |
| "JOINT LOADS - FORCE" | 8815–8818 |
| "JOINT PATTERN DEFINITIONS" | 8819–8821 |
| "JOINT RESTRAINT ASSIGNMENTS" | 8822–8878 |
| "JOINT SPRING ASSIGNMENTS 1 - UNCOUPLED" | 8879–8935 |
| "LOAD CASE DEFINITIONS" | 8936–8948 |
| "LOAD PATTERN DEFINITIONS" | 8949–8960 |
| "MASS SOURCE" | 8961–8963 |
| "MATERIAL PROPERTIES 01 - GENERAL" | 8964–8970 |
| "MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES" | 8971–8977 |
| "MATERIAL PROPERTIES 03A - STEEL DATA" | 8978–8981 |
| "MATERIAL PROPERTIES 03B - CONCRETE DATA" | 8982–8984 |
| "MATERIAL PROPERTIES 03E - REBAR DATA" | 8985–8987 |
| "MATERIAL PROPERTIES 03F - TENDON DATA" | 8988–8990 |
| "MATERIAL PROPERTIES 06 - DAMPING PARAMETERS" | 8991–8997 |
| "OPTIONS - COLORS - DISPLAY" | 8998–9008 |
| "OPTIONS - COLORS - OUTPUT" | 9009–9019 |
| "OVERWRITES - STEEL DESIGN - CSA S16-14" | 9020–12339 |
| "PREFERENCES - ALUMINUM DESIGN - AA-ASD 2000" | 12340–12342 |
| "PREFERENCES - COLD FORMED DESIGN - AISI-ASD96" | 12343–12345 |
| "PREFERENCES - CONCRETE DESIGN - ACI 318-14" | 12346–12348 |
| "PREFERENCES - DIMENSIONAL" | 12349–12351 |
| "PREFERENCES - STEEL DESIGN - CSA S16-14" | 12352–12355 |
| "PROGRAM CONTROL" | 12356–12358 |
| "PROJECT INFORMATION" | 12359–12373 |
| "REBAR SIZES" | 12374–12412 |
| "SECTION DESIGNER PROPERTIES 01 - GENERAL" | 12413–12417 |
| "SECTION DESIGNER PROPERTIES 04 - SHAPE I/WIDE FLANGE" | 12418–12421 |
| "SECTION DESIGNER PROPERTIES 07 - SHAPE ANGLE" | 12422–12427 |
| "SECTION DESIGNER PROPERTIES 09 - SHAPE BOX/TUBE" | 12428–12431 |
| "SECTION DESIGNER PROPERTIES 30 - FIBER GENERAL" | 12432–12437 |

### STRUCTURE.$et

| Section/table | Lines |
|---|---|
| PROGRAM INFORMATION | 3–5 |
| CONTROLS | 6–11 |
| STORIES - IN SEQUENCE FROM TOP | 12–19 |
| GRIDS | 20–30 |
| DIAPHRAGM NAMES | 31–33 |
| MATERIAL PROPERTIES | 34–68 |
| REBAR DEFINITIONS | 69–89 |
| FRAME SECTIONS | 90–179 |
| CONCRETE SECTIONS | 180–189 |
| SLAB PROPERTIES | 190–196 |
| DECK PROPERTIES | 197–202 |
| WALL PROPERTIES | 203–207 |
| LINK PROPERTIES | 208–212 |
| PANEL ZONE PROPERTIES | 213–215 |
| POINT SPRING PROPERTIES | 216–218 |
| PIER/SPANDREL NAMES | 219–222 |
| POINT COORDINATES | 223–226 |
| LINE CONNECTIVITIES | 227–229 |
| GROUPS | 230–233 |
| POINT ASSIGNS | 234–237 |
| LINE ASSIGNS | 238–240 |
| LOAD PATTERNS | 241–260 |
| POINT OBJECT LOADS | 261–262 |
| FRAME OBJECT LOADS | 263–268 |
| ANALYSIS OPTIONS | 269–273 |
| MASS SOURCE | 274–276 |
| FUNCTIONS | 277–284 |
| GENERALIZED DISPLACEMENTS | 285–286 |
| LOAD CASES | 287–326 |
| LOAD COMBINATIONS | 327–667 |
| STEEL DESIGN PREFERENCES | 668–680 |
| CONCRETE DESIGN PREFERENCES | 681–685 |
| COMPOSITE DESIGN PREFERENCES | 686–700 |
| WALL DESIGN PREFERENCES | 701–708 |
| DIMENSION LINES | 709–711 |
| TABLE SETS | 712–713 |
| LOG | 714–2482 |
