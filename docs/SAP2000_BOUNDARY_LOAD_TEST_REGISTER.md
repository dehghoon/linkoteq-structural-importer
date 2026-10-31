# SAP2000 boundary and load test case register

Updated: 2026-10-31. This register supplements docs/ENGINEERING_EXTRACTION_VALIDATION_STANDARD.md and docs/IMPORTER_VALIDATION_CONTRACT.md.

Executable: scripts/test_sap2000_boundary_load_known_answers.py
CI: .github/workflows/sap2000-geometry.yml
Verified successful run: https://github.com/dehghoon/linkoteq-structural-importer/actions/runs/41208060905

| Case ID | Expected result |
| --- | --- |
| SAP-BND-001 | Joint restraint six DOFs equal Yes,No,Yes,No,Yes,No |
| SAP-BND-002 | Spring stiffness equals 100.25,0,300,0,0,7.5 |
| SAP-BND-003 | Frame releases match twelve explicit expected flags |
| SAP-BND-004 | Local spring coordinates retained; transformation warning emitted |
| SAP-LOD-001 | DEAD and WIND patterns retain weight multipliers 1 and 0 |
| SAP-LOD-002 | Joint force and moment components equal -12.50,0,4,0,2.25,-3 |
| SAP-LOD-003 | Local joint force retained; warning emitted |
| SAP-NEG-001 | Invalid restraint boolean rejected |
| SAP-NEG-002 | Malformed spring numeric value rejected |
| SAP-NEG-003 | Duplicate load pattern rejected |
| SAP-NEG-004 | Duplicate frame release rejected |

All cases above passed as hand-authored synthetic known-answer or negative tests in the cited CI run. They are not independent SAP2000 vendor-oracle verification. Real-model exact values, member loads, load combinations, units, Core mapping and IFC equivalence remain unverified.

For ETABS and STAAD.Pro, reuse these semantic case categories with format-specific syntax and independently reviewed expected values.

Documentation completion gate: every newly implemented test must have a stable ID, expected behavior, evidence level, CI result URL, limitations and cross-format applicability recorded in the same PR before claiming the work is documented.

## Real-source boundary golden case (2026-10-31)

SAP-BND-REAL-001: On pinned fixture `docs/MTDENN~1.$2k` (SHA256 `8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79`), joints 51,53,57,59 have restraints (Yes,Yes,Yes,No,No,No) and Local spring stiffness (0,0,0,40000,40000,0); frames 112,131,137,138 have releases (No,No,No,No,Yes,Yes,No,No,No,No,Yes,Yes). Values transcribed from the source tables. Executable: `scripts/test_sap2000_real_boundary_golden.py`; CI: `.github/workflows/sap2000-geometry.yml`. Status: PENDING CI at registration. This tests source extraction only, not local-axis transformation or independently verified SAP2000 vendor equivalence. Further full-record coverage remains outstanding.
