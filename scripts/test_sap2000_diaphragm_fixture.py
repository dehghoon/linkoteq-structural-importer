"""Real SAP2000 diaphragm regression: definitions and node membership."""
from pathlib import Path
from hashlib import sha256
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_diaphragms import extract_diaphragms
from linkoteq_importer.import_result import build_import_result

def main():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci",namespace="ci",policy_id="read-only",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    d=extract_diaphragms(archive)
    g=extract_geometry(archive)
    ids={j.source_id for j in g.joints}
    assert any(x.source_id=="DIAPH1" for x in d.definitions)
    assert any(x.diaphragm_id=="DIAPH1" for x in d.memberships)
    assert all(x.joint_id in ids for x in d.memberships)
    result=build_import_result(archive,format="sap2000")
    assert result["sourceViews"]["diaphragms"]
    assert len(result["sourceViews"]["diaphragmMemberships"])==len(d.memberships)
    assert result["coreModel"] is None and not d.mapped_to_core
    assert archive.retrieve()==data
    print(f"PASS diaphragm definitions={len(d.definitions)} memberships={len(d.memberships)}")
if __name__=="__main__":
    main()
