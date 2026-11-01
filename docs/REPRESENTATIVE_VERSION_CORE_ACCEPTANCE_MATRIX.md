# Representative-version Core mapping acceptance matrix
Date: 2026-10-31 | Stage: implementation-ready plan; NOT an executed Core mapping test.

## Version policy and evidence
| Vendor | Historical candidate | Earlier / middle / recent test cohorts | Evidence / limitation |
| --- | --- | --- | --- |
| SAP2000 | V8 family (V6/V7 requires vendor translation) | V8; V16–20; V25–26 | CSI V6/V7 translator: https://help.csiamerica.com/help/sap2000/26/26.0.0/SAP2000/WebHelp/Menus/File/Import/Import_SAP2000_V6_or_V7_s2k_File.htm ; candidate versions are not verified importer support |
| ETABS | V13 (ETABS 2013) provisional | V13; V16–18; V21+ | CSI v13 major rewrite: http://installs.csiamerica.com/software/ETABS/2013/ReleaseNotesETABS2013v1300.pdf ; CSI v16 E2K import into v13/v15 but not v9: https://web.wiki.csiamerica.com/wiki/spaces/etabs/pages/1474770/Opening+ETABS+V16+models+in+lower+versions |
| STAAD.Pro | No defensible numeric cutoff | V8i; CONNECT V22; 2024 | Bentley .STD language reference: https://docs.bentley.com/LiveContent/web/STAAD.Pro%20Help-v2024/en/topics/Commands_TechRef/c-stpst_Commands_and_Input_Instructions.html ; compatibility is command-family based, not a blanket version guarantee |

These are **cohorts for collecting representative files**, not a statement that such files are already available. Do not infer a cutoff from software release numbers alone. SBK needs a separately evidenced grammar/compatibility determination.

## Acceptance cases at Core adapter boundary (run for each available cohort)
| Case | Source -> Core assertion | Oracle | Status |
| --- | --- | --- | --- |
| G1 | joint ID and XYZ with declared length units; frame I/J and orientation | vendor table plus manually reviewed expected Core values | NOT_IMPLEMENTED |
| M1 | E/G/nu, density vs unit weight, material references, section geometry/assignment | reviewed dimensional conversions and Core contract | NOT_IMPLEMENTED |
| B1 | six support DOFs, springs including local axes, frame I/J releases | reviewed DOF mapping and orientation | NOT_IMPLEMENTED |
| L1 | nodal/member loads, local/global directions, self weight and signed magnitudes | reviewed vector transformation and units | NOT_IMPLEMENTED |
| C1 | linear vs SRSS/modal combinations, preserve unsupported semantics | source command reference plus Core contract | NOT_IMPLEMENTED |
| F1 | provenance, unsupported/preserved-only items, no silent defaults | source archive + fidelity report | NOT_IMPLEMENTED |

**Gate:** every case reports source version, source SHA, source IDs, Core contract release, adapter commit, oracle, mapped/preserved/unsupported/invalid counts, exact/tolerance comparison, and evidence URL. Unsupported cases are NOT_IMPLEMENTED or BLOCKED, never PASS. All original source bytes retained. Source parsing regression remains lightweight; no extra random source samples required.

## Current actual evidence
SAP2000 pinned real text fixture has 388 joints, 609 frames and 84 sections and has passed source-level geometry regression; **not Core mapping**. No representative-version ETABS or STAAD fixture and no Core adapter evidence has been verified here. Next engineering action: confirm latest released Structural Core contract and implement a minimal Core adapter for geometry with G1 independently reviewed golden values before expanding to M1/B1/L1. The version policy and matrix are documentation, not proof of Core compatibility.

## First implementation: SAP2000 geometry fragment (2026-10-31)

`src/linkoteq_importer/core_geometry_fragment.py` creates a **Core v0.5-aligned geometry fragment**, with global nodes in metres, stable namespaced IDs and start/end member connectivity; rejects unknown length units and dangling references. `scripts/test_sap2000_core_geometry_fragment.py` tests synthetic feet-to-metres known answers, reversed I/J, failure cases and all 388/609 real geometry records. The workflow runs this test. **This is not a complete Core Structural Model**: material/section references and member semantics remain unresolved; `mapped_to_core=False` is intentional. G1 is PARTIAL pending actual canonical schema integration and independent reviewed oracle. Other G1 version cohorts and M1/B1/L1/C1/F1 remain NOT_IMPLEMENTED. Do not claim E4 PASS.
