# Source-specific engineering semantic converter matrix — 2026-11-01

**Status: audited implementation boundary, NOT a declaration of engineering equivalence.** Based on Import Result v0.1.0 in `gpt2/local-axes-release-contract`, Core v0.5.0. Every source is archived independently of parsing or mapping.

| Engineering concern | SAP2000 | ETABS | STAAD.Pro | Required Core adapter gate |
|---|---|---|---|---|
| Frame I/J | Parsed from CONNECTIVITY - FRAME | Preserved-only in current Import Result | Parsed MEMBER INCIDENCES | Resolve stable node IDs and verify geometry/units |
| Local 1/2/3 orientation | Source Angle extracted, global basis not verified | Preserved-only | Preserved-only | Validate handedness, angle sign and reference axis per vendor |
| End releases | P,V2,V3,T,M2,M3 flags at I and J, source-local interpretation | Preserved-only | Preserved-only | Verify vendor DOF convention and Core start/end booleans |
| Pin presets | Synthetic test releases I M2/M3 only | Preserved-only | Preserved-only | Never release translations merely because UI says pinned |
| Insertion/cardinal points | Raw table fields preserved | Preserved-only | Preserved-only | Confirm Core representation; CG-003 |
| End offsets/eccentricities | Raw archive; no validated Core conversion | Preserved-only | Preserved-only | CG-003, no invented offsets |
| Partial releases/stiffness | Source archive only; no validated converter | Preserved-only | Preserved-only | CG-003, no invented springs |
| Nodes and coordinates | Parsed in declared source units | Preserved-only | Parsed, unit declarations retained per node | Validate dimensions and unit changes |
| Materials/sections | Partial source views | Preserved-only | Preserved-only | Catalog matching with explicit uncertainty |
| Joint restraints and springs | Parsed source views | Preserved-only | Preserved-only | Verify local/global orientation and units |
| Nodal and member distributed loads | Partial source views | Preserved-only | Preserved-only | Verify directions, sign, stations and combinations |
| Diaphragms | Definitions and joint assignments extracted | Preserved-only | Preserved-only | Validate constraint type and membership; CG-004 |
| Load cases/combinations | Partial source views | Preserved-only | Preserved-only | Never equate modal/SRSS with linear superposition |

## Converter contract
- **Parser** extracts vendor-specific source entities and original units/IDs/lines.
- **Semantic converter** is vendor-specific, validates engineering meanings, and emits typed source-semantic evidence with diagnostics.
- **Core mapping adapter** promotes only validated evidence to Core. It must never infer defaults or silently discard unknown source features.
- **Import Result v0.1.0** is the shared versioned transport. All three formats expose the same `sourceViews` keys, even when the relevant list is empty. Empty views mean **not parsed/available**, not a claim that the original model lacks that feature.
- `coreModel: null` explicitly blocks claiming a validated Core model. `fidelity.originalBytesPreserved=true` does not establish engineering equivalence.
- GPT-3 must validate `contract`, `version`, `sourceFormat`, `sourceHash`, view types and local-release six-DOF flags before accepting the envelope; `src/linkoteq_importer/import_result_contract.py` provides a Python reference validator.
- Preserve unsupported and unknown source semantics in archive and report status separately. Do not transform raw source views into editable Core entities without an approved mapping.

## Acceptance gates
1. Source bytes round-trip and SHA/provenance checks.
2. Vendor-specific numeric reference fixtures for coordinate systems, I/J, local basis and sign, offsets and release DOFs.
3. Exact canonical Core serialization and reverse round-trip checks.
4. GPT-3 display/edit/save/reload tests on canonical entities plus preserved source extensions.
5. ETABS and STAAD real-format fixture coverage, not merely synthetic transport shape tests.

## Explicit gaps
CG-003 (end releases, pins and offsets), CG-004 (diaphragms), and other existing Core Gap Register entries remain OPEN; this document does not modify Core. The cross-format transport regression tests verify schema shape, not ETABS/STAAD converter completion.
