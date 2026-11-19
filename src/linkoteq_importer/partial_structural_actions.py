"""Attach source-provenanced boundaries and loads to a partial visual model.

No silent transformations: local springs/loads are retained in source coordinates.
No claim of Core-valid analysis input.
"""
from .partial_structural_model import build_partial_model

def build_partial_model_with_actions(geometry,properties,boundaries,loads,*,
                                     stress_unit,density_unit,length_unit):
    hashes={geometry.source_hash,properties.source_hash,
            boundaries.source_hash,loads.source_hash}
    if len(hashes)!=1:raise ValueError("SOURCE_HASH_MISMATCH")
    result=build_partial_model(geometry,properties,stress_unit=stress_unit,
                               density_unit=density_unit,length_unit=length_unit)
    node_ids={n["sourceId"] for n in result["nodes"]}
    member_ids={m["sourceId"] for m in result["members"]}
    pattern_ids={p.source_id for p in loads.patterns}
    issues=list(result["diagnostics"])+list(boundaries.diagnostics)+list(loads.diagnostics)
    restraints=[]
    for r in boundaries.restraints:
        if r.joint_id not in node_ids:
            issues.append("UNKNOWN_RESTRAINT_NODE:"+r.joint_id);continue
        restraints.append({"nodeId":"sap2000:node:"+r.joint_id,
                           "fixed":list(r.fixed),"sourceLine":r.source_line})
    springs=[]
    for s in boundaries.springs:
        if s.joint_id not in node_ids:
            issues.append("UNKNOWN_SPRING_NODE:"+s.joint_id);continue
        springs.append({"nodeId":"sap2000:node:"+s.joint_id,
                        "sourceCoordinateSystem":s.coordinate_system,
                        "sourceStiffness":[str(v) for v in s.stiffness],
                        "sourceLine":s.source_line,"coreMapped":False})
    releases=[]
    for r in boundaries.releases:
        if r.frame_id not in member_ids:
            issues.append("UNKNOWN_RELEASE_MEMBER:"+r.frame_id);continue
        releases.append({"memberId":"sap2000:member:"+r.frame_id,
                         "sourceReleased":[bool(v) for v in r.released],
                         "sourceLine":r.source_line,"coreMapped":False})
    forces=[]
    for f in loads.joint_forces:
        if f.joint_id not in node_ids:
            issues.append("UNKNOWN_LOAD_NODE:"+f.joint_id);continue
        if f.pattern_id not in pattern_ids:
            issues.append("UNKNOWN_LOAD_PATTERN:"+f.pattern_id)
        forces.append({"nodeId":"sap2000:node:"+f.joint_id,
                       "patternId":"sap2000:load-pattern:"+f.pattern_id,
                       "sourceCoordinateSystem":f.coordinate_system,
                       "sourceComponents":[str(v) for v in f.components],
                       "sourceLine":f.source_line,"coreMapped":False})
    result["restraints"]=restraints
    result["sourceSprings"]=springs
    result["sourceFrameReleases"]=releases
    result["sourceLoadPatterns"]=[{"id":"sap2000:load-pattern:"+p.source_id,
                                   "designType":p.design_type,
                                   "sourceSelfWeightMultiplier":str(p.self_weight_multiplier),
                                   "sourceLine":p.source_line} for p in loads.patterns]
    result["sourceJointForces"]=forces
    result["diagnostics"]=issues
    result["kind"]="partial-structural-model-with-source-boundaries-and-loads"
    result["mapped_to_core"]=False
    result["analysisReady"]=False
    return result
