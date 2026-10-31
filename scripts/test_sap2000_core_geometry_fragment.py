"""Core v0.5 geometry fragment acceptance: source-independent known answers and real fixture."""
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.core_geometry_fragment import map_geometry_fragment
from linkoteq_importer.sap2000_geometry import GeometryView,Joint,Frame,extract_geometry
from linkoteq_importer.preservation import Limits,archive_bytes

def check_known_answers():
    view=GeometryView(
        (Joint("10",Decimal("12"),Decimal("-2"),Decimal("0"),1),
         Joint("20",Decimal("15"),Decimal("4"),Decimal("6"),2)),
        (Frame("B", "20","10",3),),"synthetic","KIP_ft_F",())
    fragment=map_geometry_fragment(view)
    assert fragment["nodes"]==[
        {"id":"sap2000:node:10","sourceId":"10","x":"3.6576","y":"-0.6096","z":"0.00000"},
        {"id":"sap2000:node:20","sourceId":"20","x":"4.5720","y":"1.2192","z":"1.8288"}]
    assert fragment["members"]==[
        {"id":"sap2000:member:B","sourceId":"B",
         "startNodeId":"sap2000:node:20","endNodeId":"sap2000:node:10"}]
    assert fragment["mapped_to_core"] is False
    for units in (None,"unknown"):
        try: map_geometry_fragment(GeometryView(view.joints,view.frames,"x",units,()))
        except ValueError: pass
        else: raise AssertionError("unknown units silently accepted")
    try:
        map_geometry_fragment(GeometryView(view.joints,(Frame("bad","10","missing",3),),
                                           "x","KN_m_C",()))
    except ValueError: pass
    else: raise AssertionError("dangling reference silently accepted")

def check_real():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    geometry=extract_geometry(archive)
    result=map_geometry_fragment(geometry)
    assert len(result["nodes"])==388 and len(result["members"])==609
    factor=Decimal("1") if result["units"]["length"]=="m" else None
    assert factor is not None
    nodes={n["sourceId"]:n for n in result["nodes"]}
    for j in geometry.joints:
        n=nodes[j.source_id]
        # Use source-unit conversion as independently established in synthetic test.
        from linkoteq_importer.core_geometry_fragment import length_factor
        k=length_factor(geometry.declared_units)
        assert tuple(Decimal(n[axis]) for axis in ("x","y","z"))==(
            j.x*k,j.y*k,j.z*k)
    for f,m in zip(geometry.frames,result["members"]):
        assert m["startNodeId"]=="sap2000:node:"+f.joint_i
        assert m["endNodeId"]=="sap2000:node:"+f.joint_j
    assert result["mapped_to_core"] is False
    print("PASS Core geometry fragment: 388 nodes, 609 members; NOT complete Core model")

if __name__=="__main__":
    check_known_answers()
    check_real()
