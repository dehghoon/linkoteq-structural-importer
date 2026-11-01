"""Synthetic malformed-reference regression for SAP diaphragm source view."""
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_diaphragms import extract_diaphragms

def main():
    source=b'''TABLE: "JOINT COORDINATES"
Joint=1 CoordSys=GLOBAL CoordType=Cartesian XorR=0 Y=0 Z=0

TABLE: "CONSTRAINT DEFINITIONS - DIAPHRAGM"
Name=D1 CoordSys=GLOBAL Axis=Z MultiLevel=No

TABLE: "JOINT CONSTRAINT ASSIGNMENTS"
Joint=1 Constraint=D1
Joint=1 Constraint=D1
Joint=99 Constraint=D1
Joint=1 Constraint=OTHER

END TABLE DATA
'''
    limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)
    archive=archive_bytes(source,filename="synthetic.s2k",extension=".s2k",
        project_ref="ci",namespace="ci",policy_id="test",limits=limits)
    d=extract_diaphragms(archive)
    assert len(d.definitions)==1 and len(d.memberships)==4
    assert any(x.startswith("DUPLICATE_JOINT_CONSTRAINT_ASSIGNMENT:") for x in d.diagnostics)
    assert any(x.startswith("DIAPHRAGM_MEMBERSHIP_UNKNOWN_JOINT:") for x in d.diagnostics)
    assert any(x.startswith("JOINT_CONSTRAINT_NOT_DIAPHRAGM_DEFINITION:") for x in d.diagnostics)
    assert archive.retrieve()==source
    print("PASS diaphragm invalid-reference diagnostics",d.diagnostics)

if __name__=="__main__":
    main()
