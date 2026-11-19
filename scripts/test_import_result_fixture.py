"""Real SAP fixture: Import Result contract, determinism, IDs, no false Core claims."""
import json
from pathlib import Path
from hashlib import sha256
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.import_result import build_import_result

limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)

def main():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",limits=limits)
    a=build_import_result(archive,format="sap2000")
    b=build_import_result(archive,format="sap2000")
    assert json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)
    assert a["version"]=="0.1.0" and a["coreModel"] is None
    assert a["stages"]["mapped"]=="not-attempted"
    assert len(a["sourceViews"]["nodes"])==388
    assert len(a["sourceViews"]["frames"])==609
    assert len(a["sourceViews"]["sections"])==84
    assert a["sourceViews"]["loadCombinations"]
    ids=[item["id"] for group in a["sourceViews"].values() for item in group]
    assert len(ids)==len(set(ids)), "duplicate Import Result entity IDs"
    assert archive.retrieve()==data
    print("PASS Import Result v0.1.0",json.dumps({k:len(v) for k,v in a["sourceViews"].items()},sort_keys=True))

    opaque=archive_bytes(b"$ File header\nUNKNOWN COMMAND\n",filename="sample.$et",
        extension=".$et",project_ref="ci",namespace="ci",policy_id="test",limits=limits)
    etabs=build_import_result(opaque,format="etabs")
    assert etabs["coreModel"] is None and etabs["stages"]["parsed"]=="not-attempted"
    assert etabs["sourceViews"]["nodes"]==[] and opaque.retrieve().startswith(b"$")
    print("PASS ETABS preserved-only Import Result (not parsed)")
if __name__=="__main__":
    main()
