"""Run SAP2000 boundary/load extraction against the pinned real source fixture."""
from pathlib import Path
from hashlib import sha256
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.sap2000_loads import extract_loads

def main():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    geometry=extract_geometry(archive)
    boundary=extract_boundaries(archive)
    loads=extract_loads(archive)
    joints={j.source_id for j in geometry.joints}
    frames={f.source_id for f in geometry.frames}
    assert all(x.joint_id in joints for x in boundary.restraints)
    assert all(x.joint_id in joints for x in boundary.springs)
    assert all(x.frame_id in frames for x in boundary.releases)
    assert all(x.joint_id in joints for x in loads.joint_forces)
    assert boundary.restraints and boundary.springs and boundary.releases
    assert loads.patterns and loads.joint_forces
    assert archive.retrieve()==data
    assert not boundary.mapped_to_core and not loads.mapped_to_core
    print(f"PASS: restraints={len(boundary.restraints)} springs={len(boundary.springs)} releases={len(boundary.releases)} patterns={len(loads.patterns)} nodal_forces={len(loads.joint_forces)}")
    print("DIAGNOSTICS:",*(boundary.diagnostics+loads.diagnostics)[:20],sep="\n")
if __name__=="__main__":
    main()
