from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_grid_preview import project_source_grid_preview


def test_unnamed_cartesian_grid_has_explicit_display_identity_and_preserves_source():
    data = b'''TABLE: "GRID LINES"
CoordSys=GLOBAL AxisDir=Y XRYZCoord=3.2
CoordSys=GLOBAL AxisDir=X GridID=K XRYZCoord=1.5
CoordSys=LOCAL AxisDir=X GridID=E1 XRYZCoord=2
END TABLE DATA
'''
    archive = archive_bytes(data, filename="synthetic.s2k", extension=".s2k",
                            project_ref="synthetic", namespace="sap2000",
                            policy_id="preserve-source",
                            limits=Limits(20000000,200000,200000,2000000,200000,300000,300000,100000000))
    preview = project_source_grid_preview(archive)
    assert len(preview["gridLines"]) == 2
    unnamed, named = preview["gridLines"]
    assert unnamed["sourceIdentifierMissing"] is True
    assert unnamed["displayLabel"] == "Unnamed Y grid"
    assert named["id"] == "K"
    assert named["sourceIdentifierMissing"] is False
    assert len(preview["deferredGridLines"]) == 1
    assert archive.retrieve() == data
    assert preview["analysisReady"] is False
