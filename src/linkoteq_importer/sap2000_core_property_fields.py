"""SAP2000 source field mapping to SI; explicit field names and dimensions only.

No inferred Poisson ratio, shear modulus, density or section properties.
CSI material mass/weight density are distinct. Missing required fields block.
"""
from decimal import Decimal
from .core_geometry_fragment import length_factor
from .core_property_values import material_si,section_si
from .sap2000_properties import CatalogEntry,PropertyView

def _fields(entry:CatalogEntry):
    fields={}
    for key,value in entry.fields:
        key=key.casefold()
        if key in fields: raise ValueError("DUPLICATE_PROPERTY_FIELD:"+key)
        fields[key]=value
    return fields

def _required(f,*names):
    for name in names:
        if name not in f: raise ValueError("MISSING_SOURCE_PROPERTY:"+name)
    return [f[n] for n in names]

def source_material_to_si(entry:CatalogEntry, *,stress_unit:str,
                          density_unit:str)->dict:
    f=_fields(entry)
    # SAP2000 isotropic material details typically use E1, G12, U12.
    # This adapter requires a reviewed explicit schema and does not guess
    # aliases from unrelated material family definitions.
    e,g,nu=_required(f,"e1","g12","u12")
    if "unitmass" in f:
        rho=f["unitmass"]
    elif "masspervol" in f:
        rho=f["masspervol"]
    elif "unitweight" in f or "weightpervol" in f:
        raise ValueError("WEIGHT_DENSITY_REQUIRES_EXPLICIT_GRAVITY_CONVERSION")
    else:
        raise ValueError("MISSING_MASS_DENSITY")
    return {"sourceId":entry.source_id,**material_si(
        E=e,G=g,nu=nu,rho=rho,stress_unit=stress_unit,density_unit=density_unit)}

def source_section_to_si(entry:CatalogEntry, *,length_unit:str)->dict:
    f=_fields(entry)
    a,iy,iz,j=_required(f,"area","i22","i33","torsconst")
    return {"sourceId":entry.source_id,**section_si(
        A=a,Iy=iy,Iz=iz,J=j,length_unit=length_unit)}

def map_reviewed_properties(view:PropertyView, *,stress_unit:str,
                            density_unit:str,length_unit:str)->dict:
    materials=[];sections=[];unmapped=[]
    for item in view.material_details:
        f=_fields(item)
        if all(k in f for k in ("e1","g12","u12")):
            try:materials.append(source_material_to_si(item,stress_unit=stress_unit,
                                                       density_unit=density_unit))
            except ValueError as e:unmapped.append("MATERIAL:"+item.source_id+":"+str(e))
    for item in view.sections:
        try:sections.append(source_section_to_si(item,length_unit=length_unit))
        except ValueError as e:unmapped.append("SECTION:"+item.source_id+":"+str(e))
    return {"materials":materials,"sections":sections,"unmapped":unmapped,
            "mapped_to_core":False,
            "status":"REVIEW_REQUIRED_NOT_CORE_ACCEPTED"}
