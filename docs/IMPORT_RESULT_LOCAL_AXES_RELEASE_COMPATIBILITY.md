# GPT-2 / GPT-3 Engineering Compatibility — Import Result 0.1.0

Status: **candidate / source evidence only / not Core-mapped**. Repository `dehghoon/linkoteq-structural-importer`, branch `gpt2/local-axes-release-contract`, based on `gpt2/sap2000-engineering-geometry` at `50cb83b840fbb5913132f545732bc6b684c3e54e`. Neither branch is merged into main.

## Actual source and producer
- `src/linkoteq_importer/import_result.py`: `build_import_result(archive, format="sap2000"|"staad"|"etabs", limits=...)`.
- `src/linkoteq_importer/sap2000_frame_axes.py`: angle and insertion source views.
- `src/linkoteq_importer/sap2000_boundary.py`: SAP releases, 12 flags ordered `PI,V2I,V3I,TI,M2I,M3I,PJ,V2J,V3J,TJ,M2J,M3J`.
- `src/linkoteq_importer/sap2000_release_semantics.py`: I/J local DOF interpretation.
- `scripts/test_sap2000_release_semantics.py`: **synthetic, explicitly authored test**, not claimed to be a real SAP export.
- `docs/MTDENN~1.$2k`: real SAP2000 source fixture; tests independently cover local-axis rotations and release references.

## Exact JSON contract (relevant subset)
```json
{
  "contract": "linkoteq.import-result",
  "version": "0.1.0",
  "coreContract": "v0.5.0",
  "sourceFormat": "sap2000",
  "coreModel": null,
  "sourceViews": {
    "nodes": [],
    "frames": [],
    "releases": [],
    "frameAxisRotations": [],
    "frameInsertions": [],
    "frameEndReleaseSemantics": [
      {
        "id": "<deterministic-source-id>",
        "sourceId": "B1",
        "sourceLine": 1,
        "sourceHash": "<archive-hash>",
        "frameSourceId": "B1",
        "startReleaseLocal": {"U1": false, "U2": false, "U3": false, "R1": false, "R2": true, "R3": true},
        "endReleaseLocal": {"U1": false, "U2": false, "U3": false, "R1": false, "R2": false, "R3": false},
        "localAxisAngleDegrees": "90",
        "status": "source-local-interpretation-not-core-mapped",
        "warnings": []
      }
    ]
  }
}
```
The excerpt illustrates fields and values from the **synthetic authored test**, not a full emitted fixture or actual source line/hash. `true` means **released** (not restrained). Local U1/U2/U3 correspond to SAP P/V2/V3; R1/R2/R3 to T/M2/M3. Start = SAP I, end = SAP J. The angle is a source decimal string. The `id` and `sourceLine` above are placeholders; consumers must use actual emitted values.

## Core mapping and gap matrix
| SAP source | Core v0.5 | Current status |
|---|---|---|
| Frame JointI / JointJ | Member startNodeId / endNodeId | Source IDs preserved; canonical IDs and unit transform not validated |
| Angle | Member rotationDeg / localAxes | Source degrees preserved; sign, reference vector, global orientation not validated |
| PI,V2I,V3I,TI,M2I,M3I | Member startRelease U1,U2,U3,R1,R2,R3 | Source-local flags interpreted; Core serializer not validated |
| PJ,V2J,V3J,TJ,M2J,M3J | Member endRelease U1,U2,U3,R1,R2,R3 | Source-local flags interpreted; Core serializer not validated |
| CardinalPt, Mirror2/3, Transform | Insertion/offset representation | Preserved source fields; Core standard mapping not verified; CG-003 |
| Partial release and stiffness | Per-DOF release/spring | Not parsed; archive preserved; CG-003 |
| ETABS and STAAD axes/releases | Member orientation/releases | Not validated; source archive only |

Core contract states local +x runs from start to end and axes are right-handed. **Do not** treat source angle alone as a validated right-handed Core `localAxes` vector or convert M2/M3 to global rotations without source-specific transformation validation.

## GPT-3 consumer requirements
- Manual editor must work independently of import; do not derive canonical model from `sourceViews` without approved adapter.
- Never swap R2/R3, I/J, or flip release booleans. Pinned-I in this test releases only R2/R3; translational DOFs remain connected.
- Preserve insertion/offset data as source evidence even if not editable.
- No silent assumptions for missing angle, cardinal point, partial stiffness, ETABS/STAAD semantics.
- Save/Open round-trip and graphical axis display must be tested by GPT-3; importer CI cannot certify UI.
- Regression contract: run `PYTHONPATH=src python scripts/test_sap2000_release_semantics.py` and real SAP `scripts/test_sap2000_frame_axes_fixture.py`. CI link must be attached only after successful run.

## Coordination and outstanding blockers
Core Gap Register: `dehghoon/linkoteq-structural-core/docs/CORE_GAP_REGISTER.md`, especially CG-003. Core schema must not be changed by GPT-2. Pending: source-specific right-handed basis and sign validation, end offsets, partial releases, ETABS and STAAD mappings, complete Core serializer and real Import→3D→Save/Open acceptance.
