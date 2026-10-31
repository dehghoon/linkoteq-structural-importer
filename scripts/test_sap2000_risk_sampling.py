"""Exercise risk selector against real SAP2000 boundary records and synthetic coverage cases."""
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.risk_sampling import Candidate,select_samples

def main():
    sample=[
        Candidate("A",("ordinary","local"),("local",)),
        Candidate("B",("ordinary",)),
        Candidate("C",("local","spring"),("local","spring")),
        Candidate("D",("spring",),("spring",)),
    ]
    result=select_samples(sample)
    assert not result.uncovered
    assert result.target_by_class=={"ordinary":1,"local":2,"spring":2}
    assert len(result.selected_ids)==3,result
    assert result==select_samples(reversed(sample))
    try:
        select_samples([Candidate("A",("x",)),Candidate("A",("y",))])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate ID not rejected")
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    b=extract_boundaries(archive)
    candidates=[]
    for x in b.restraints:
        classes=("restraint","restraint_mixed" if any(x.fixed) and not all(x.fixed) else "restraint_other")
        candidates.append(Candidate("restraint:"+x.joint_id,classes,("restraint_mixed",) if classes[1]=="restraint_mixed" else ()))
    for x in b.springs:
        classes=("spring","spring_local" if x.coordinate_system.casefold()!="global" else "spring_global",
                 "spring_rotational" if any(x.stiffness[3:]) else "spring_no_rotation")
        high=tuple(v for v in classes if v in ("spring_local","spring_rotational"))
        candidates.append(Candidate("spring:"+x.joint_id,classes,high))
    for x in b.releases:
        classes=("release","release_any" if any(x.released) else "release_none")
        candidates.append(Candidate("release:"+x.frame_id,classes,("release_any",) if classes[1]=="release_any" else ()))
    result=select_samples(candidates)
    assert result.selected_ids and not result.uncovered
    assert len(result.selected_ids)<len(candidates)
    assert all(result.class_counts[k]>=v for k,v in result.target_by_class.items())
    print("PASS: deterministic SAP2000 boundary risk selection",len(candidates),"records",len(result.selected_ids),"samples")
    print("SELECTED:",",".join(result.selected_ids))
    print("CLASS COUNTS:",result.class_counts)

if __name__=="__main__":
    main()
