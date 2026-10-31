"""Build a usable *partial* structural model without dropping source members.

Unresolved properties are explicitly tagged and remain visible in the
geometry. This is not an analysis-ready Core v0.5 model.
"""
from .core_property_references import bind_property_references
from .sap2000_core_property_fields import map_reviewed_properties

def build_partial_model(geometry,properties,*,stress_unit,density_unit,length_unit):
    bound=bind_property_references(geometry,properties)
    values=map_reviewed_properties(properties,stress_unit=stress_unit,
                                   density_unit=density_unit,length_unit=length_unit)
    sections={v["sourceId"]:v for v in values["sections"]}
    materials={v["sourceId"]:v for v in values["materials"]}
    by_member={}
    for diagnostic in bound["unresolvedReferences"]:
        _,member_id,*detail=diagnostic.split(":")
        by_member.setdefault(member_id,[]).append(diagnostic)
    members=[]
    for member in bound["members"]:
        m=dict(member);problems=list(by_member.get(m["sourceId"],[]))
        sid=m.get("sectionId","").removeprefix("sap2000:section:")
        mid=m.get("materialId","").removeprefix("sap2000:material:")
        if sid and sid not in sections:problems.append("SECTION_PROPERTIES_NOT_MAPPED:"+sid)
        if mid and mid not in materials:problems.append("MATERIAL_PROPERTIES_NOT_MAPPED:"+mid)
        m["mappingStatus"]="partial" if problems else "property-values-mapped"
        m["diagnostics"]=problems
        members.append(m)
    return {"contract":bound["contract"],
            "kind":"partial-structural-model-not-analysis-ready",
            "sourceHash":bound["sourceHash"],"units":bound["units"],
            "coordinateSystem":bound["coordinateSystem"],
            "nodes":bound["nodes"],"members":members,
            "sectionProperties":values["sections"],
            "materialProperties":values["materials"],
            "unresolvedReferences":bound["unresolvedReferences"],
            "unmappedProperties":values["unmapped"],
            "diagnostics":list(properties.diagnostics),
            "mapped_to_core":False,"analysisReady":False}
