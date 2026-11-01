# Core advanced-contract compatibility handoff (GPT-2)

Status: PENDING CONSUMER VERIFICATION — not a claim of importer runtime compatibility.
Core verified CI commit: 3077831d330b9e81751b50b4d1e32679ff2ca9be
Core schema discriminator: 0.5 (unchanged)
Core documents:
- docs/CORE_ADVANCED_SEMANTICS_V06.md
- docs/CORE_V05_TO_V06_MIGRATION.md

This handoff supplements, not replaces, docs/CORE_IMPORT_GAP_ANALYSIS.md. Its original baseline b1f25a6... is historical. The importer project-status.json is likewise historical until independently reconciled.

Required source-specific semantic verification:
1. SAP2000: members/releases, nodal links/MPCs, joists, surface axes, shell results, diaphragms and load signs.
2. ETABS: same categories with story-relative coordinate and diaphragm semantics.
3. STAAD.Pro: units changes, ranges, releases, local axes, joists, shells and preservation of unsupported commands.

For each feature classify: mapped, preserved-only, unsupported or invalid; record source IDs, units, source bytes, lossless archive and fidelity diagnostics. Do not auto-enable new Core capabilities merely because the type exists. Keep PyNite behind Core Analysis Adapter.

Acceptance requires real format fixtures, deterministic stable IDs, physical force/moment invariants, no loss of source data, and explicit Core SHA pin. Existing CI success without these fixtures does not satisfy this handoff.

Next action for GPT-2: run its Core drift/compatibility gates against this SHA, document individual capability evidence and update project-status.json only after verification.
