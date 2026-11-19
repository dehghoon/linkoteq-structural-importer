"""Real SAP frame local axes and release association regression."""
from pathlib import Path
from hashlib import sha256
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_frame_axes import extract_frame_axes
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.import_result import build_import_result

def main():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci",namespace="ci",policy_id="test",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    axes=extract_frame_axes(archive)
    boundary=extract_boundaries(archive)
    frames={f.source_id for f in extract_geometry(archive).frames}
    assert axes.rotations and axes.insertions
    assert any(r.angle_degrees==90 for r in axes.rotations)
    assert all(a.frame_id in frames for a in axes.rotations+axes.insertions)
    assert all(r.frame_id in frames for r in boundary.releases)
    result=build_import_result(archive,format="sap2000")
    assert len(result["sourceViews"]["frameAxisRotations"])==len(axes.rotations)
    assert len(result["sourceViews"]["frameInsertions"])==len(axes.insertions)
    assert result["capabilities"]["frameLocalAxes"]=="source-angle-only-not-transformed"
    assert result["coreModel"] is None and archive.retrieve()==data
    print("PASS source frame axes",len(axes.rotations),"insertions",len(axes.insertions),"releases",len(boundary.releases))

if __name__=="__main__":
    main()
