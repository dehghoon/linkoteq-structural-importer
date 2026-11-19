"""Synthetic known-answer regression for SAP2000 boundary and nodal-load semantics.

Independent, hand-authored expected values; not a vendor-verified real-model oracle.
"""
from decimal import Decimal
from linkoteq_importer.preservation import Limits, archive_bytes, ArchiveError
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.sap2000_loads import extract_loads

LIMITS = Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)

def parse(source):
    data = source.encode("utf-8")
    archive = archive_bytes(data,filename="synthetic.$2k",extension=".$2k",
        project_ref="known-answer",namespace="ci",policy_id="read-only",limits=LIMITS)
    return extract_boundaries(archive), extract_loads(archive)

def reject(source, prefix):
    try:
        parse(source)
    except ArchiveError as exc:
        assert str(exc).startswith(prefix), (prefix, str(exc))
    else:
        raise AssertionError("Expected " + prefix)

def main():
    source = """TABLE: "JOINT RESTRAINT ASSIGNMENTS"
 Joint=J1 U1=Yes U2=No U3=Yes R1=No R2=Yes R3=No
TABLE: "JOINT SPRING ASSIGNMENTS 1 - UNCOUPLED"
 Joint=J2 CoordSys=Global U1=100.25 U2=0 U3=300 R1=0 R2=0 R3=7.5
 Joint=J3 CoordSys=Local U1=1 U2=2 U3=3 R1=4 R2=5 R3=6
TABLE: "FRAME RELEASE ASSIGNMENTS 1 - GENERAL"
 Frame=F1 PI=Yes V2I=No V3I=No TI=No M2I=Yes M3I=Yes PJ=No V2J=No V3J=No TJ=Yes M2J=No M3J=Yes
TABLE: "LOAD PATTERN DEFINITIONS"
 LoadPat=DEAD DesignType=Dead SelfWtMult=1
 LoadPat=WIND DesignType=Wind SelfWtMult=0
TABLE: "JOINT LOADS - FORCE"
 Joint=J1 LoadPat=WIND CoordSys=Global F1=-12.50 F2=0 F3=4 M1=0 M2=2.25 M3=-3
 Joint=J2 LoadPat=DEAD CoordSys=Local F1=1 F2=2 F3=3 M1=4 M2=5 M3=6
"""
    boundary, loads = parse(source)
    assert len(boundary.restraints) == 1
    assert boundary.restraints[0].joint_id == "J1"
    assert boundary.restraints[0].fixed == (True,False,True,False,True,False)
    assert [(s.joint_id,s.coordinate_system,s.stiffness) for s in boundary.springs] == [
        ("J2","Global",tuple(map(Decimal,["100.25","0","300","0","0","7.5"]))),
        ("J3","Local",tuple(map(Decimal,["1","2","3","4","5","6"])))]
    assert boundary.releases[0].released == (True,False,False,False,True,True,False,False,False,True,False,True)
    assert [(p.source_id,p.design_type,p.self_weight_multiplier) for p in loads.patterns] == [
        ("DEAD","Dead",Decimal("1")),("WIND","Wind",Decimal("0"))]
    assert [(f.joint_id,f.pattern_id,f.coordinate_system,f.components) for f in loads.joint_forces] == [
        ("J1","WIND","Global",tuple(map(Decimal,["-12.50","0","4","0","2.25","-3"]))),
        ("J2","DEAD","Local",tuple(map(Decimal,["1","2","3","4","5","6"])))]
    assert any("SPRING_LOCAL_AXES_REQUIRE_TRANSFORM" in x for x in boundary.diagnostics)
    assert any("JOINT_FORCE_NON_GLOBAL_COORDSYS" in x for x in loads.diagnostics)
    assert not boundary.mapped_to_core and not loads.mapped_to_core

    reject('TABLE: "JOINT RESTRAINT ASSIGNMENTS"\n Joint=J1 U1=Maybe U2=No U3=No R1=No R2=No R3=No\n',
           "SAP_INVALID_BOOLEAN:")
    reject('TABLE: "JOINT SPRING ASSIGNMENTS 1 - UNCOUPLED"\n Joint=J2 CoordSys=Global U1=abc U2=0 U3=0 R1=0 R2=0 R3=0\n',
           "SAP_INVALID_COORDINATE:")
    reject('TABLE: "LOAD PATTERN DEFINITIONS"\n LoadPat=DEAD SelfWtMult=1\n LoadPat=DEAD SelfWtMult=0\n',
           "SAP_DUPLICATE_OR_MISSING_LOAD_PATTERN:")
    reject('TABLE: "FRAME RELEASE ASSIGNMENTS 1 - GENERAL"\n Frame=F1 PI=No V2I=No V3I=No TI=No M2I=No M3I=No PJ=No V2J=No V3J=No TJ=No M2J=No M3J=No\n Frame=F1 PI=No V2I=No V3I=No TI=No M2I=No M3I=No PJ=No V2J=No V3J=No TJ=No M2J=No M3J=No\n',
           "SAP_DUPLICATE_OR_MISSING_RELEASE:")
    print("PASS: synthetic boundary/load exact-value known answers and four negative cases")

if __name__ == "__main__":
    main()
