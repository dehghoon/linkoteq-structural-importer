"""Bind SAP2000 section/material identities to Core geometry fragment.

Identity mapping only. No invented section A/Iy/Iz/J or material E/G/rho.
This is NOT a complete Core model and cannot be used for analysis.
"""
from __future__ import annotations
from .sap2000_geometry import GeometryView
from .sap2000_properties import PropertyView
from .core_geometry_fragment import map_geometry_fragment

def bind_property_references(geometry:GeometryView, properties:PropertyView)->dict:
    if geometry.source_hash != properties.source_hash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    result=map_geometry_fragment(geometry)
    sections={s.source_id:s for s in properties.sections}
    materials={m.source_id:m for m in properties.materials}
    assignments={}
    for a in properties.assignments:
        if a.frame_id in assignments:
            raise ValueError("AMBIGUOUS_FRAME_SECTION_ASSIGNMENT:"+a.frame_id)
        assignments[a.frame_id]=a
    unresolved=[]
    for member in result["members"]:
        source=member["sourceId"]
        a=assignments.get(source)
        if a is None:
            unresolved.append("MISSING_SECTION_ASSIGNMENT:"+source)
            continue
        section=sections.get(a.section_id)
        if section is None:
            unresolved.append("UNKNOWN_SECTION:"+source+":"+a.section_id)
            continue
        member["sectionId"]="sap2000:section:"+a.section_id
        section_fields={k.casefold():v for k,v in section.fields}
        material_id=a.material_override or next(
            (v for k,v in section_fields.items() if k.casefold()=="material"),None)
        if not material_id or material_id not in materials:
            unresolved.append("UNRESOLVED_MATERIAL:"+source+":"+(material_id or ""))
            continue
        member["materialId"]="sap2000:material:"+material_id
    result["sectionReferences"]=[{"id":"sap2000:section:"+s.source_id,
                                   "sourceId":s.source_id,
                                   "sourceLine":s.source_line}
                                  for s in properties.sections]
    result["materialReferences"]=[{"id":"sap2000:material:"+m.source_id,
                                    "sourceId":m.source_id,
                                    "sourceLine":m.source_line}
                                   for m in properties.materials]
    result["unresolvedReferences"]=unresolved
    result["unmappedRequiredMemberFields"]=["sectionProperties:A,Iy,Iz,J",
                                               "materialProperties:E,G,nu,rho"]
    result["kind"]="geometry-and-property-reference-fragment-not-analysis-ready"
    result["mapped_to_core"]=False
    return result
