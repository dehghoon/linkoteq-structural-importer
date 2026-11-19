"""Read-only pinned real SAP2000 file: report mapped and preserved-only properties.

The report is an inventory of attempted source-field conversion, not Core E4
acceptance. Never guess units or fabricate missing section properties.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_properties import extract_properties
from linkoteq_importer.sap2000_core_property_fields import map_reviewed_properties
from linkoteq_importer.core_property_references import bind_property_references

def run():
    p=Path("docs/MTDENN~1.$2k")
    data=p.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=archive_bytes(data,filename=p.name,extension=p.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    geometry=extract_geometry(archive)
    props=extract_properties(archive)
    # The real fixture declares KN, m, C. kN/m2 is kPa. Mass density in
    # source is not automatically assumed to be kg/m3; this is an
    # intentionally provisional, explicitly chosen conversion context.
    result=map_reviewed_properties(props,stress_unit="kPa",
                                   density_unit="kg/m3",length_unit="m")
    bound=bind_property_references(geometry,props)
    assert len(geometry.joints)==388 and len(geometry.frames)==609
    assert len(props.sections)==84 and len(props.assignments)==609
    assert len(result["sections"])+sum(x.startswith("SECTION:") for x in result["unmapped"])==84
    assert len(bound["members"])==609
    assert not result["mapped_to_core"] and not bound["mapped_to_core"]
    counts=Counter(x.split(":")[-1] for x in result["unmapped"])
    print("REAL FIXTURE PROPERTY FIELD COVERAGE")
    print("mapped_section_values",len(result["sections"]))
    print("mapped_material_detail_values",len(result["materials"]))
    print("unmapped_count",len(result["unmapped"]))
    print("unmapped_reasons",dict(sorted(counts.items())))
    print("unresolved_member_references",len(bound["unresolvedReferences"]))
    print("extractor_diagnostics",list(props.diagnostics))
    print("STATUS: PRESERVED_ONLY where unsupported; NOT CORE E4 ACCEPTED")

if __name__=="__main__":run()
