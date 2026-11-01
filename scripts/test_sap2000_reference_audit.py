"""Reference audit regression using actual SAP2000 and malformed synthetic model."""
from pathlib import Path
from hashlib import sha256
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_reference_audit import audit_references
from linkoteq_importer.import_result import build_import_result

LIMITS=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)

def make(data,name):
    return archive_bytes(data,filename=name,extension=".s2k",
        project_ref="ci",namespace="ci",policy_id="test",limits=LIMITS)

def main():
    data=Path("docs/MTDENN~1.$2k").read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=make(data,"fixture.s2k")
    a=audit_references(archive)
    result=build_import_result(archive,format="sap2000")
    assert a.counts["nodes"]==388 and a.counts["frames"]==609
    assert result["referenceAudit"]["diagnostics"]==list(a.diagnostics)
    assert not a.mapped_to_core and result["coreModel"] is None
    assert archive.retrieve()==data
    print("PASS real SAP reference audit",a.counts,"issues",len(a.diagnostics))
    source=b'''TABLE: "JOINT COORDINATES"
Joint=1 CoordSys=GLOBAL CoordType=Cartesian XorR=0 Y=0 Z=0

TABLE: "CONNECTIVITY - FRAME"
Frame=1 JointI=1 JointJ=1

TABLE: "JOINT RESTRAINT ASSIGNMENTS"
Joint=99 U1=Yes U2=Yes U3=Yes R1=No R2=No R3=No

TABLE: "FRAME RELEASE ASSIGNMENTS 1 - GENERAL"
Frame=99 PI=No V2I=No V3I=No TI=No M2I=Yes M3I=Yes PJ=No V2J=No V3J=No TJ=No M2J=Yes M3J=Yes

TABLE: "LOAD PATTERN DEFINITIONS"
LoadPat=DEAD DesignType=Dead SelfWtMult=1

TABLE: "JOINT LOADS - FORCE"
Joint=99 LoadPat=DEAD CoordSys=GLOBAL F1=0 F2=0 F3=-1 M1=0 M2=0 M3=0

END TABLE DATA
'''
    broken=make(source,"invalid.s2k")
    report=audit_references(broken)
    assert any(x.startswith("RESTRAINT_UNKNOWN_JOINT:") for x in report.diagnostics)
    assert any(x.startswith("RELEASE_UNKNOWN_FRAME:") for x in report.diagnostics)
    assert any(x.startswith("JOINT_LOAD_UNKNOWN_JOINT:") for x in report.diagnostics)
    assert broken.retrieve()==source
    print("PASS invalid SAP reference audit",report.diagnostics)

if __name__=="__main__":
    main()
