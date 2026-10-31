"""Risk-stratified SAP2000 material, section and assignment selection on pinned real data."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json
from linkoteq_importer.preservation import Limits,archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_properties import extract_properties
from linkoteq_importer.risk_sampling import Candidate,select_samples

HASH="8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
def classify(view,geometry):
    frame_ids={f.source_id for f in geometry.frames}
    materials={m.source_id for m in view.materials}
    sections={s.source_id for s in view.sections}
    candidates=[]
    for item in view.materials:
        f={k.casefold():v for k,v in item.fields}
        cls=["material","material_custom" if any("user" in v.casefold() for v in f.values()) else "material_catalog"]
        candidates.append(Candidate("material:"+item.source_id,tuple(cls),
                                    ("material_custom",) if "material_custom" in cls else ()))
    for item in view.sections:
        f={k.casefold():v for k,v in item.fields}
        cls=["section"]
        if f.get("material") not in materials: cls.append("section_unknown_material")
        if any("nonprismatic" in v.casefold() or "sectiondesigner" in v.casefold() for v in f.values()):
            cls.append("section_complex")
        if len(cls)==1: cls.append("section_regular")
        high=tuple(x for x in cls if x in ("section_unknown_material","section_complex"))
        candidates.append(Candidate("section:"+item.source_id,tuple(cls),high))
    for index,item in enumerate(view.assignments):
        cls=["assignment"]
        if item.frame_id not in frame_ids: cls.append("assignment_unknown_frame")
        if item.section_id not in sections: cls.append("assignment_unknown_section")
        if item.material_override: cls.append("assignment_material_override")
        if len(cls)==1: cls.append("assignment_regular")
        high=tuple(x for x in cls if x.startswith("assignment_unknown") or x=="assignment_material_override")
        # Stable unique identity even when repeated assignment for the same frame is present.
        candidates.append(Candidate("assignment:"+str(index).zfill(6)+":"+item.frame_id,tuple(cls),high))
    return candidates

def main():
    path=Path("docs/MTDENN~1.$2k")
    data=path.read_bytes()
    assert sha256(data).hexdigest()==HASH
    archive=archive_bytes(data,filename=path.name,extension=path.suffix,
        project_ref="ci-fixture",namespace="ci",policy_id="read-only",
        limits=Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000))
    view=extract_properties(archive)
    geometry=extract_geometry(archive)
    assert len(view.sections)==84
    candidates=classify(view,geometry)
    assert len(candidates)==len(view.materials)+len(view.sections)+len(view.assignments)
    result=select_samples(candidates)
    assert result.selected_ids and not result.uncovered
    assert result==select_samples(reversed(candidates))
    for cls,target in result.target_by_class.items():
        assert sum(cls in result.reasons[sid] for sid in result.selected_ids)>=target
    report={"format":"SAP2000","domain":"materials_sections_assignments",
        "source_sha256":HASH,"total_records":len(candidates),
        "materials":len(view.materials),"sections":len(view.sections),
        "assignments":len(view.assignments),"class_counts":result.class_counts,
        "target_by_class":result.target_by_class,"selected_ids":result.selected_ids,
        "reasons":result.reasons,"uncovered":result.uncovered,
        "status":"SELECTED_NOT_INDEPENDENTLY_REVIEWED",
        "limitations":["Heuristic classification only; no numeric modulus/density boundary analysis",
                       "No independently verified vendor golden values",
                       "No full-record exact source cross-check for properties",
                       "No pairwise interaction or negative-case generation"]}
    Path("risk-properties-selection.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PASS property risk selection:",len(candidates),"records;",len(result.selected_ids),"samples")
    print("SELECTED:",",".join(result.selected_ids))
    print("CLASS COUNTS:",result.class_counts)

if __name__=="__main__":
    main()
