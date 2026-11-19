"""Contract test: explicit synthetic SAP table, not a real SAP-export claim."""
import json
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.sap2000_frame_axes import extract_frame_axes
from linkoteq_importer.sap2000_release_semantics import interpret_release
from linkoteq_importer.import_result import build_import_result

SYNTHETIC_SAP=b'''TABLE: "JOINT COORDINATES"
Joint=I CoordSys=GLOBAL CoordType=Cartesian XorR=0 Y=0 Z=0
Joint=J CoordSys=GLOBAL CoordType=Cartesian XorR=5 Y=0 Z=0

TABLE: "CONNECTIVITY - FRAME"
Frame=B1 JointI=I JointJ=J

TABLE: "FRAME LOCAL AXES ASSIGNMENTS 1 - TYPICAL"
Frame=B1 Angle=90

TABLE: "FRAME INSERTION POINT ASSIGNMENTS"
Frame=B1 CardinalPt="10 (centroid)" Mirror2=No Mirror3=No Transform=Yes

TABLE: "FRAME RELEASE ASSIGNMENTS 1 - GENERAL"
Frame=B1 PI=No V2I=No V3I=No TI=No M2I=Yes M3I=Yes PJ=No V2J=No V3J=No TJ=No M2J=No M3J=No

END TABLE DATA
'''

def main():
    limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)
    archive=archive_bytes(SYNTHETIC_SAP,filename="synthetic-pin-i-fixed-j.s2k",
        extension=".s2k",project_ref="ci",namespace="ci",policy_id="test",limits=limits)
    boundary=extract_boundaries(archive)
    axes=extract_frame_axes(archive)
    assert len(boundary.releases)==1 and len(axes.rotations)==1
    semantic=interpret_release(boundary.releases[0],axes)
    assert semantic.start==dict(zip(("U1","U2","U3","R1","R2","R3"),(False,False,False,False,True,True)))
    assert semantic.end==dict.fromkeys(("U1","U2","U3","R1","R2","R3"),False)
    assert semantic.local_axis_angle_degrees=="90"
    result=build_import_result(archive,format="sap2000")
    view=result["sourceViews"]["frameEndReleaseSemantics"]
    assert len(view)==1 and view[0]["startReleaseLocal"]==semantic.start
    assert view[0]["endReleaseLocal"]==semantic.end
    assert result["coreModel"] is None
    assert archive.retrieve()==SYNTHETIC_SAP
    assert json.dumps(result,sort_keys=True)==json.dumps(build_import_result(archive,format="sap2000"),sort_keys=True)
    print("PASS synthetic pinned-I fixed-J 90-degree local-axis source contract")

if __name__=="__main__":
    main()
