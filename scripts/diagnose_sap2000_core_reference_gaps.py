"""Diagnose unresolved real SAP2000 member references without guessing defaults."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_properties import extract_properties
from linkoteq_importer.core_property_references import bind_property_references

def run():
    p=Path("docs/MTDENN~1.$2k"); data=p.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    a=archive_bytes(data,filename=p.name,extension=p.suffix,project_ref="ci-fixture",
                    namespace="ci",policy_id="read-only",
                    limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    g=extract_geometry(a);p=extract_properties(a)
    mapped=bind_property_references(g,p)
    reasons=Counter(x.split(":")[0] for x in mapped["unresolvedReferences"])
    print("UNRESOLVED_MEMBER_REFERENCE_COUNTS",dict(sorted(reasons.items())))
    print("UNRESOLVED_MEMBER_REFERENCE_EXAMPLES",mapped["unresolvedReferences"][:15])
    print("UNRESOLVED_MEMBER_REFERENCE_TOTAL",len(mapped["unresolvedReferences"]))
    print("MATERIAL_SOURCE_FIELD_INVENTORY")
    for m in p.materials:
        print("MATERIAL",m.source_id,"general_keys",sorted({k.casefold() for k,v in m.fields}))
    for d in p.material_details:
        print("DETAIL",d.source_id,"keys",sorted({k.casefold() for k,v in d.fields}))
    print("SOURCE_ARCHIVED",a.retrieve()==data)
    assert len(mapped["members"])==609
    assert a.retrieve()==data
    print("STATUS DIAGNOSTIC ONLY; NOT CORE ACCEPTED")

if __name__=="__main__":run()
