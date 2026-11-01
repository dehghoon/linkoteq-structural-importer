"""Pinned real SAP2000 boundary golden values, manually transcribed from source tables.

This is a source-to-parser regression, NOT vendor-verified engineering equivalence.
"""
from pathlib import Path
from hashlib import sha256
from decimal import Decimal
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_boundary import extract_boundaries

def main():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    b=extract_boundaries(archive)
    restraints={r.joint_id:r for r in b.restraints}
    springs={s.joint_id:s for s in b.springs}
    releases={r.frame_id:r for r in b.releases}
    for joint in ("51","53","57","59"):
        assert restraints[joint].fixed==(True,True,True,False,False,False),joint
        assert springs[joint].coordinate_system=="Local",joint
        assert springs[joint].stiffness==tuple(map(Decimal,("0","0","0","40000","40000","0"))),joint
    for frame in ("112","131","137","138"):
        assert releases[frame].released==(False,False,False,False,True,True,False,False,False,False,True,True),frame
    assert any("SPRING_LOCAL_AXES_REQUIRE_TRANSFORM" in x for x in b.diagnostics)
    assert archive.retrieve()==data
    assert not b.mapped_to_core
    print("PASS: pinned real-source boundary golden values (4 joints, 4 frames); local spring transform not validated")

if __name__=="__main__":
    main()
