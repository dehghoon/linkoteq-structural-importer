"""Core v0.5 geometry fragment adapter: not a complete Structural Model.

Nodes are global, member start/end follow SAP I/J. Member material/section
references are unresolved, so this fragment MUST NOT be treated as a valid
complete Core model or analysis-ready payload.
"""
from __future__ import annotations
from decimal import Decimal
from .sap2000_geometry import GeometryView

_LENGTH_TO_M={"m":Decimal("1"),"mm":Decimal("0.001"),"cm":Decimal("0.01"),
              "ft":Decimal("0.3048"),"in":Decimal("0.0254")}

def length_factor(declared_units: str | None) -> Decimal:
    if not declared_units:
        raise ValueError("UNDECLARED_SOURCE_UNITS")
    # CSI unit declarations are force_length_temperature, e.g. KN_m_C.
    parts=declared_units.casefold().replace("-", "_").replace(",", "_").split("_")
    matches=[part for part in parts if part in _LENGTH_TO_M]
    if len(matches)!=1:
        raise ValueError("UNSUPPORTED_LENGTH_UNITS:"+declared_units)
    return _LENGTH_TO_M[matches[0]]

def map_geometry_fragment(view:GeometryView)->dict:
    if any(x.startswith(("UNRESOLVED_FRAME_JOINT","CONFLICTING_DECLARED_UNITS"))
           for x in view.diagnostics):
        raise ValueError("SOURCE_GEOMETRY_DIAGNOSTICS:"+",".join(view.diagnostics))
    factor=length_factor(view.declared_units)
    ids={j.source_id for j in view.joints}
    if len(ids)!=len(view.joints):
        raise ValueError("DUPLICATE_JOINT")
    if len({f.source_id for f in view.frames})!=len(view.frames):
        raise ValueError("DUPLICATE_FRAME")
    if any(f.joint_i not in ids or f.joint_j not in ids for f in view.frames):
        raise ValueError("DANGLING_FRAME")
    nodes=[{"id":"sap2000:node:"+j.source_id,"sourceId":j.source_id,
            "x":str(j.x*factor),"y":str(j.y*factor),"z":str(j.z*factor)}
           for j in view.joints]
    members=[{"id":"sap2000:member:"+f.source_id,"sourceId":f.source_id,
              "startNodeId":"sap2000:node:"+f.joint_i,
              "endNodeId":"sap2000:node:"+f.joint_j}
             for f in view.frames]
    return {"contract":"Linkoteq Structural Core v0.5",
            "kind":"geometry-fragment-not-analysis-ready",
            "units":{"length":"m"},"coordinateSystem":"global",
            "sourceHash":view.source_hash,"nodes":nodes,"members":members,
            "unmappedRequiredMemberFields":["materialId","sectionId"],
            "mapped_to_core":False}
