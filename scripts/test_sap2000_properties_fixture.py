"""Read-only pinned real-fixture regression for SAP2000 material/section extraction."""
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_properties import extract_properties
from linkoteq_importer.sap2000_geometry import extract_geometry

def main():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",limits=limits)
    view=extract_properties(archive)
    geometry=extract_geometry(archive)
    assert len(view.sections)==84, len(view.sections)
    assert view.materials, "no materials"
    assert view.assignments, "no assignments"
    known_frames={f.source_id for f in geometry.frames}
    dangling=[a.frame_id for a in view.assignments if a.frame_id not in known_frames]
    assert not dangling, f"unknown assigned frames: {dangling[:10]}"
    assert archive.retrieve()==data
    assert not view.mapped_to_core
    print(f"PASS: materials={len(view.materials)} sections={len(view.sections)} assignments={len(view.assignments)} details={len(view.material_details)} diagnostics={len(view.diagnostics)}")
    for diagnostic in view.diagnostics[:20]:
        print("DIAGNOSTIC:",diagnostic)
if __name__=="__main__":
    main()
