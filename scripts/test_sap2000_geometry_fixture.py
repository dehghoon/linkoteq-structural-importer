"""SAP2000 engineering geometry smoke/regression on the pinned real fixture."""
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits, archive_bytes, ArchiveError
from linkoteq_importer.sap2000_geometry import extract_geometry

def main():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    expected="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    assert sha256(data).hexdigest()==expected, "SOURCE_HASH_MISMATCH"
    limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",limits=limits)
    view=extract_geometry(archive)
    assert len(view.joints)==388, f"joints={len(view.joints)}"
    assert len(view.frames)==609, f"frames={len(view.frames)}"
    assert view.declared_units=="KN, m, C", view.declared_units
    assert not view.mapped_to_core
    assert archive.retrieve()==data
    assert not view.diagnostics, view.diagnostics
    print(f"PASS: joints={len(view.joints)} frames={len(view.frames)} units={view.declared_units}; core mapping not attempted")
if __name__=="__main__":
    main()
