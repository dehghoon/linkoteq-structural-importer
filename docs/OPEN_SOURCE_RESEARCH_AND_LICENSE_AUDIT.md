# Open-source research and license audit

Version: 0.1 — 2026-10-28. Status: source-level research, not dependency approval.

No third-party tests were executed. No vulnerability scan, coverage measurement, performance benchmark, legal clearance, or production compatibility validation was performed. Source inspection establishes implementation evidence, not working end-to-end behavior. All recommendations are conditional.

## 1. ebrahimraeyat/etabs_api

1. **Owner/URL:** [ebrahimraeyat/etabs_api](https://github.com/ebrahimraeyat/etabs_api).
2. **Revision evaluated:** `1f3cf94b8b11964ca9c17f721d0166c61413aba1`, default branch master, commit 2026-08-31.
3. **License:** actual LICENSE contains GNU Library General Public License version 2, June 1991. GitHub metadata says NOASSERTION. Exact file-level grant and any later-version permission need review; do not label this MIT or GPL3.
4. **Distribution compatibility:** unresolved for intended commercial packaging; LGPL2 compliance strategy and legal review required before copying, adaptation or distribution.
5. **Actual formats:** CSI API automation plus an offline E2K reader for units, stories, points, line/area definitions, assignments, sections and materials. No verified complete .$et support.
6. **Implementation evidence:** [e2k_reader.py](https://github.com/ebrahimraeyat/etabs_api/blob/1f3cf94b8b11964ca9c17f721d0166c61413aba1/e2k_reader.py) inspected. It handles doubled quotes but explicitly disclaims full semantics. Replacement decoding, skipped records, a default zero z and one stored units tuple fail the proposed preservation contract unchanged.
7. **Tests:** [test/test_e2k_reader.py](https://github.com/ebrahimraeyat/etabs_api/blob/1f3cf94b8b11964ca9c17f721d0166c61413aba1/test/test_e2k_reader.py) has minimal synthetic E2K and quoted-string assertions; read, not run. Coverage unknown.
8. **Maintenance:** latest inspected default-branch commit 2026-08-31; repository not archived.
9. **Dependencies/security:** offline reader imports pandas; broader desktop/API dependencies need full inventory. Malformed-token fallback and replacement decoding require review. No CVE scan.
10. **Proprietary requirements:** inspected offline reader does not invoke ETABS; wider API automation requires CSI software.
11. **Isolation:** offline module appears separable; confirm imports and licenses before extraction.
12. **Integration cost:** moderate/high for byte provenance, unit-state tracking, diagnostics and Core mapping; estimate, not measured effort.
13. **Performance/scalability:** unbenchmarked; no approved file-size or entity-count envelope.
14. **Recommendation:** reference now; possible wrap/adapt after license strategy and engineering validation.

## 2. SeismoVLAB/SVL

1. **Owner/URL:** [SeismoVLAB/SVL](https://github.com/SeismoVLAB/SVL).
2. **Revision:** `f07d55cec2b2a8cf612a1069fd8d0700790e7836`, master, 2024-12-12.
3. **License:** root LICENSE includes GPL version 3 and additional third-party licenses; file-level scope requires review.
4. **Distribution compatibility:** proprietary reuse not approved. A separate service does not automatically resolve GPL obligations.
5. **Formats:** limited E2K and S2K readers; SAP reader also handles links. Not full source semantics.
6. **Evidence:** inspected [SAP2000.py](https://github.com/SeismoVLAB/SVL/blob/f07d55cec2b2a8cf612a1069fd8d0700790e7836/01-Pre_Process/Parser/SAP2000.py) and [ETABS.py](https://github.com/SeismoVLAB/SVL/blob/f07d55cec2b2a8cf612a1069fd8d0700790e7836/01-Pre_Process/Parser/ETABS.py); actual token parsing and SAP underscore continuations present. Positional assumptions and unsupported records prevent adoption unchanged.
7. **Tests:** validation directory exists; parser-specific coverage and passing results unverified.
8. **Maintenance:** inspected latest branch commit 2024-12-12; not archived.
9. **Dependencies/security:** NumPy, SVL internal modules, whole-file reads, replacement decoding and positional loops. Malformed input/resource limits and dependencies not audited.
10. **Proprietary requirements:** text readers themselves do not call CSI.
11. **Isolation:** medium; internal model/utilities coupling.
12. **Integration cost:** high for preservation and canonical semantics.
13. **Performance:** no measurements; whole-file memory use visible.
14. **Recommendation:** reference only; no copying without approved GPL strategy.

## 3. alvin-yang68/SAP2000-to-Ruaumoko

1. **Owner/URL:** [alvin-yang68/SAP2000-to-Ruaumoko](https://github.com/alvin-yang68/SAP2000-to-Ruaumoko).
2. **Revision:** `5e0208a8df82d7d299f5f03ce4f20a1a2fa36e0f`, main, 2020-12-04.
3. **License:** metadata null; no license file in inspected complete tree. Reuse permission not established.
4. **Distribution compatibility:** cannot approve copying or derivative use without permission.
5. **Formats:** S2K to Ruaumoko text, primarily geometry. README names frames, braces and springs as direct equivalents; other entities become generic members requiring manual properties.
6. **Evidence:** [converter.py](https://github.com/alvin-yang68/SAP2000-to-Ruaumoko/blob/5e0208a8df82d7d299f5f03ce4f20a1a2fa36e0f/converter.py) inspected; joins underscore continuations and builds table records.
7. **Tests:** no dedicated tests discovered; working execution unverified.
8. **Maintenance:** latest inspected commit 2020-12-04.
9. **Dependencies/security:** tkinter GUI, pickle serialization and app-specific modules; brittle line indexing and delimiter parsing. Never accept untrusted pickle. No scan.
10. **Proprietary requirements:** source export originates in SAP2000; converter reads text without observed API invocation.
11. **Isolation:** GUI and global-module coupling make extraction less straightforward.
12. **Integration cost:** high; unsuitable as complete importer.
13. **Performance:** no benchmarks or scale evidence.
14. **Recommendation:** reference only; reject copying/adoption without explicit license.

## 4. BHoM/SAP2000_Toolkit

1. **Owner/URL:** [BHoM/SAP2000_Toolkit](https://github.com/BHoM/SAP2000_Toolkit).
2. **Revision:** `ce9ab48d5156d404ee2e0991bfe466e87e50ea40`, develop, 2026-09-25.
3. **License:** inspected LICENSE is LGPL v3; README agrees.
4. **Distribution compatibility:** conditional on LGPL compliance and packaging review; not cleared.
5. **Formats/functionality:** BHoM/SAP2000 API object interoperability; offline S2K grammar not established. README intends SAP v21+ and reports testing exclusively on v23.
6. **Evidence:** [README](https://github.com/BHoM/SAP2000_Toolkit/blob/ce9ab48d5156d404ee2e0991bfe466e87e50ea40/README.md), repository CRUD/conversion paths for bars, nodes, panels, loads, sections, materials and results.
7. **Tests:** CI compliance scripts discovered; engineering test outcomes/coverage unverified.
8. **Maintenance:** branch commit 2026-09-25; repository pushed 2026-10-19, not archived.
9. **Dependencies/security:** C#/.NET, BHoM ecosystem and SAP API. Dependency and automation-process audit outstanding.
10. **Proprietary requirements:** SAP2000 installation/API expected; exact supported deployment licensing not reviewed.
11. **Isolation:** poor fit for standalone Python text parsing; reusable conceptual mapping boundary.
12. **Integration cost:** high for initial importer.
13. **Performance:** no benchmarks.
14. **Recommendation:** reference only for initial offline service; optional separate API interoperability work later.

## 5. IfcOpenShell/IfcOpenShell

1. **Owner/URL:** [IfcOpenShell/IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell).
2. **Revision:** `f7ff1a2b210328e38d08892efd3724dfaf99150b`, v0.9.0 branch, 2026-10-28. Research pin, not selected production release.
3. **License:** COPYING.LESSER is LGPL v3; [component table](https://github.com/IfcOpenShell/IfcOpenShell/blob/f7ff1a2b210328e38d08892efd3724dfaf99150b/README.md) describes Python library as LGPL-3.0-or-later with component caveats. Bonsai is GPL-3.0-or-later. Do not assign one license to the entire monorepo.
4. **Distribution compatibility:** preferred conditional option; selected package, native dependencies, notices, source/relinking requirements and distribution model need legal review.
5. **Formats:** IFC parsing/manipulation, including IFC4 Add2 TC1 per README. Not an E2K/S2K/STD parser.
6. **Evidence:** Python API, `src/ifcopenshell-python/ifcopenshell/validate.py` and documented model authoring ecosystem.
7. **Tests:** `test/test_validate.py`, `test_validate_rocksdb.py` and IFC test workflows discovered; not executed.
8. **Maintenance:** current inspected commit 2026-10-28; active repository.
9. **Dependencies/security:** native C++ and geometry stack, platform wheels; require SBOM, package pinning, vulnerability scan and bounded native-parser isolation.
10. **Proprietary requirements:** no proprietary CAD needed for core library.
11. **Isolation:** good Python exporter/validator wrapper boundary.
12. **Integration cost:** moderate library integration, substantial semantic mapping and validation.
13. **Performance:** no measured limits; geometry and validation must be benchmarked.
14. **Recommendation:** preferred conditional wrapper candidate, subject to stable package selection, legal compliance and golden IFC tests.

## 6. buildingSMART resources

1. **Owner/URL:** [buildingSMART/Standards-builds](https://github.com/buildingSMART/Standards-builds), official published IFC specifications.
2. **Revision/release:** repository `adf59ef789441cfbc92012a9d2126234d56c6175`, main, 2026-10-27; normative target IFC4 ADD2 TC1 / 4.0.2.1, October 2017, ISO 16739-1:2018 as listed by official index.
3. **License:** metadata null; README distinguishes reserved rights before formal release from CC BY-ND 4.0 for final IFC. Individual artifact copyright exceptions apply.
4. **Distribution compatibility:** reference released standards with attribution; no assumption of reusable implementation code or permission to redistribute altered specifications.
5. **Formats/functionality:** published EXPRESS, XSD and documentation; normative resource, not executable parser.
6. **Evidence:** [schema index](https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/), [IFC4 ADD2 TC1 schemas](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/annex/annex-a.htm), [license statement](https://technical.buildingsmart.org/standards/IFC/).
7. **Tests:** schema/conformance resources; not evidence of importer test coverage.
8. **Maintenance:** build repository active October 2026; use released IFC4 baseline rather than mutable preview standards.
9. **Dependencies/security:** no executable component adopted. External validation upload privacy and schema artifact integrity must be considered.
10. **Proprietary requirements:** none for reference use.
11. **Isolation:** pin released schema artifacts/version independently of build tooling.
12. **Integration cost:** moderate schema/mapping work.
13. **Performance:** not applicable to documentation; chosen validator needs benchmarks.
14. **Recommendation:** normative reference only, respecting exact artifact licenses. No blanket code reuse permission established.

## 7. JWock82/Pynite

1. **Owner/URL:** verified [JWock82/Pynite](https://github.com/JWock82/Pynite); proposed `pyNite/PyNite` identity not assumed.
2. **Revision:** `e3a0bbd912b6cf13140f01ca0ed3a2ee55069f45`, main, 2026-10-25.
3. **License:** inspected MIT, copyright D. Craig Brinck.
4. **Distribution compatibility:** permissive candidate subject to notice retention and transitive dependency audit; no blanket legal clearance.
5. **Formats/functionality:** structural solver, not vendor text importer. README advertises static elastic, P-Delta, frame modal and steel pushover.
6. **Evidence:** [README](https://github.com/JWock82/Pynite/blob/e3a0bbd912b6cf13140f01ca0ed3a2ee55069f45/README.md) and extensive solver/test paths. Upstream features do not enlarge Core v0.5 adapter authority automatically.
7. **Tests:** Testing directory includes releases, loads, rotation, springs, settlement, PDelta benchmarks and modal tests; build/test workflow found. No execution or current CI result verified.
8. **Maintenance:** latest inspected commit 2026-10-25; active repository.
9. **Dependencies/security:** exact dependency inventory/CVEs not audited; numerical validity and resource exhaustion controls required.
10. **Proprietary requirements:** no proprietary solver required.
11. **Isolation:** mandatory existing Core Analysis Adapter; never call directly from frontend or vendor parser.
12. **Integration cost:** moderate adapter capability/version verification; analysis outside initial importer scope.
13. **Performance:** no model-size or memory benchmarks.
14. **Recommendation:** retain/reference only through approved Core Adapter; pin compatible solver version and verify each supported capability.

## 8. DannCarlo/OpenBuilding — additional STAAD candidate

1. **Owner/URL:** [DannCarlo/OpenBuilding](https://github.com/DannCarlo/OpenBuilding).
2. **Revision:** `7b72284e05cde46bbd0fefbf21531da9888ca988`, main, 2026-08-10.
3. **License:** inspected MIT, copyright OpenBuilding 2026.
4. **Distribution compatibility:** potentially adaptable with notices; catalog/data licensing separate and not verified.
5. **Formats:** standalone TypeScript STAAD .std reader; .sbk support/equivalence not validated.
6. **Evidence:** [STAAD parser](https://github.com/DannCarlo/OpenBuilding/blob/7b72284e05cde46bbd0fefbf21531da9888ca988/src/parser/staad/index.ts), command modules and public sample RC/steel STD files. Geometry, materials, properties, supports, groups, offsets, beta and continuations visible. Critical defect against this contract: all joints are normalized using the final stored length unit, so mixed-unit handling requires redesign. Unknown blocks skipped; meter/kN defaults initialized.
7. **Tests:** samples found; automated parser tests not found in inspected test-name inventory. No test execution.
8. **Maintenance:** latest inspected commit 2026-08-10.
9. **Dependencies/security:** steel database and section-profile coupling; catalog provenance, dependencies and malformed-input behavior unaudited.
10. **Proprietary requirements:** no STAAD runtime for inspected parser.
11. **Isolation:** moderate; parser tied to profiles/catalogs.
12. **Integration cost:** high for Python port, unit state, full provenance, loading and strict semantics.
13. **Performance:** browser parser unbenchmarked.
14. **Recommendation:** selective adaptation research after validation; reject unchanged adoption as authoritative engine.

## 9. BentleySystems/openstaadpy — additional STAAD validation candidate

1. **Owner/URL:** [BentleySystems/openstaadpy](https://github.com/BentleySystems/openstaadpy).
2. **Revision:** `233a74351e4903c0e0fc01bd1ef6ad11b584b87a`, main, 2026-09-29.
3. **License:** inspected MIT, Bentley Systems.
4. **Distribution compatibility:** wrapper permissive with notices; proprietary STAAD runtime terms are separate and unreviewed.
5. **Formats/functionality:** Python COM access to running STAAD.Pro; not offline STD/SBK grammar.
6. **Evidence:** [README](https://github.com/BentleySystems/openstaadpy/blob/233a74351e4903c0e0fc01bd1ef6ad11b584b87a/README.md) requires Windows 11+, STAAD.Pro 2025+ installed/running, Python 3.11+, valid STAAD license.
7. **Tests:** Tests/README.md found; coverage and pass results unverified.
8. **Maintenance:** commit 2026-09-29; repository pushed 2026-10-05.
9. **Dependencies/security:** COM/desktop process automation; dependency scan, automation isolation and runtime licensing not reviewed.
10. **Proprietary requirements:** valid installed/running STAAD.Pro mandatory.
11. **Isolation:** separate Windows validation harness feasible; not independent hosted text parser.
12. **Integration cost:** high for infrastructure and licensed validation environment.
13. **Performance:** unbenchmarked.
14. **Recommendation:** optional validation-oracle research; not production importer dependency.

## Adoption gates and licensing controls

The [GNU license FAQ](https://www.gnu.org/licenses/gpl-faq.en.html) was consulted for linking/distribution distinctions; this report grants no legal clearance. GPT-4 must establish intended SaaS/on-premises/client distribution before final decisions. Keep notices and obtain applicable review for GPL/LGPL usage. No-license source is not reusable merely because public.

Before adoption: select stable production release and artifact hashes; inventory direct/transitive/native dependencies and catalog assets; generate SBOM and license/notice inventory; inspect file-level grants; scan vulnerabilities; run representative and malformed-input fixtures in isolation; measure time/memory across bounded input sizes; record exact CI and package evidence. No candidate currently proves full-fidelity E2K/S2K/STD/SBK conversion. No private user model was uploaded or used in this research.
