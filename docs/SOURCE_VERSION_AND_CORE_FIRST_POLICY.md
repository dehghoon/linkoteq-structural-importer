# Source-format version policy and Core-first validation plan
Date: 2026-10-31 | Status: provisional; no unverified minimum versions asserted.

## Decision
Treat vendor exports as authoritative source data. Do not revalidate vendor structural calculations. Keep only lightweight format/version detection, basic readability and safety checks, and explicit unsupported-version/feature diagnostics. Prioritize source-to-Core semantic equivalence, including units, axes, identifiers, material/section properties, loads, supports and releases. Original bytes and unsupported content must remain preserved.

## Evidence-backed boundaries
- **SAP2000:** CSI documents a distinct V6/V7 text format requiring translation to V8. Reject **recognized V6/V7 legacy-format** files with actionable upgrade guidance. **V8+ is a historical candidate family, NOT an assertion of full importer support**; supported table variants must be evidenced with fixtures and parser/Core adapter capability. Source: https://help.csiamerica.com/help/sap2000/26/26.0.0/SAP2000/WebHelp/Menus/File/Import/Import_SAP2000_V6_or_V7_s2k_File.htm
- **ETABS:** E2K text export is documented, but no defensible numeric minimum version has yet been established. Do not invent one. Source: https://docs.csiamerica.com/help-files/etabs/Menus/File/Export/Export.htm
- **STAAD.Pro:** STD command-language input is documented; version-specific command support needs a compatibility matrix. No defensible minimum version or SBK version boundary established. Source: https://docs.bentley.com/LiveContent/web/STAAD.Pro%20Help-v20/en/GUID-CA1320D6-24AA-4949-9F13-2C8E3CA390E4.html

## Runtime decision
Known incompatible legacy format -> UNSUPPORTED_FORMAT_VERSION with vendor conversion guidance. Known tested version/feature family -> process with explicit coverage. Unknown/missing version -> do not guess compatibility or silently discard records; preserve source, inspect supported syntax and report UNKNOWN_FORMAT_VERSION / UNSUPPORTED_FEATURE as appropriate. Do not reject solely because version metadata is absent if the format can be safely recognized. A vendor export may legitimately contain only selected tables or objects; never equate valid export with complete model. Source: https://help.csiamerica.com/help/sap2000/26/26.0.0/SAP2000/WebHelp/Menus/File/Export/Export_SAP2000_s2k_Text_File.htm

## Test allocation
1. **Lightweight input gate:** version/format family recognition, encoding/readability, size limits, unsupported legacy signature, missing required references; keep existing smoke tests.
2. **Core mapping gate (priority):** explicit source ID -> Core ID provenance; exact/converted values with dimensional tolerances; unit and coordinate transforms; DOFs/releases/springs; material/section dimensions and assignments; loads/combinations including SRSS; fidelity classification for unsupported semantics. Add independent known-answer cases at the Core adapter boundary.
3. **Downstream:** IFC and engineering-equivalence checks are separate; never infer them from parser success.

## Current implementation caveat
SAP2000 geometry, properties, boundary and load extractors currently expose source views with mapped_to_core=False. Existing risk-sampling scripts are retained as optional diagnostics/regression tools, **not** Core mapping acceptance gates. No Core equivalence is yet claimed. Before implementing a hard version rejection in code, verify exact detectable source signature and regression fixtures for that format family; this document does not authorize arbitrary numeric thresholds.
