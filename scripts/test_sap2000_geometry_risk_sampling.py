"""Risk-stratified samples for every joint and frame in the real SAP2000 fixture."""
from __future__ import annotations
from collections import Counter
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import json
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.risk_sampling import Candidate,select_samples

PATH=Path("docs/MTDENN~1.$2k")
HASH="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"

def classify(geometry):
    joints={j.source_id:j for j in geometry.joints}
    usage=Counter(k for f in geometry.frames for k in (f.joint_i,f.joint_j))
    candidates=[]
    for j in geometry.joints:
        cls=["joint","joint_negative" if min(j.x,j.y,j.z)<0 else "joint_nonnegative"]
        if any(v==0 for v in (j.x,j.y,j.z)): cls.append("joint_zero_coordinate")
        if usage[j.source_id]>=4: cls.append("joint_high_connectivity")
        high=tuple(c for c in cls if c in ("joint_negative","joint_high_connectivity"))
        candidates.append(Candidate("joint:"+j.source_id,tuple(cls),high))
    for f in geometry.frames:
        a,b=joints.get(f.joint_i),joints.get(f.joint_j)
        if a is None or b is None:
            raise AssertionError("dangling frame joint: "+f.source_id)
        dx,dy,dz=b.x-a.x,b.y-a.y,b.z-a.z
        sq=dx*dx+dy*dy+dz*dz
        cls=["frame"]
        if sq==0: cls.append("frame_zero_length")
        elif sum(v!=0 for v in (dx,dy,dz))>=2: cls.append("frame_inclined")
        else: cls.append("frame_axis_aligned")
        if dx<0 or dy<0 or dz<0: cls.append("frame_negative_direction")
        high=tuple(c for c in cls if c in ("frame_zero_length","frame_inclined","frame_negative_direction"))
        candidates.append(Candidate("frame:"+f.source_id,tuple(cls),high))
    return candidates

def main():
    data=PATH.read_bytes()
    assert sha256(data).hexdigest()==HASH
    archive=archive_bytes(data,filename=PATH.name,extension=PATH.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    geometry=extract_geometry(archive)
    assert len(geometry.joints)==388 and len(geometry.frames)==609
    assert not any(x.startswith("UNRESOLVED_FRAME_JOINT") for x in geometry.diagnostics)
    candidates=classify(geometry)
    result=select_samples(candidates)
    assert not result.uncovered
    assert len(candidates)==997
    assert len(result.selected_ids)<len(candidates)
    assert result==select_samples(reversed(candidates))
    for cls,target in result.target_by_class.items():
        actual=sum(cls in result.reasons[sid] for sid in result.selected_ids)
        assert actual>=target,(cls,target,actual)
    report={"format":"SAP2000","domain":"joint_frame_geometry","source_sha256":HASH,
        "total_records":len(candidates),"joint_records":len(geometry.joints),
        "frame_records":len(geometry.frames),"class_counts":result.class_counts,
        "target_by_class":result.target_by_class,"selected_ids":result.selected_ids,
        "reasons":result.reasons,"uncovered":result.uncovered,
        "status":"SELECTED_NOT_INDEPENDENTLY_REVIEWED",
        "limitations":["No independently verified golden oracle","No local-axis/offset semantics",
                       "No near-duplicate proximity threshold","No boundary/pairwise generation"]}
    output=Path("risk-geometry-selection.json")
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PASS deterministic geometry selection:",len(candidates),"records;",len(result.selected_ids),"selected")
    print("SELECTED:",",".join(result.selected_ids))
    print("CLASS COUNTS:",result.class_counts)

if __name__=="__main__":
    main()
