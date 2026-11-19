"""Fail-closed dimensional material/section property conversion to SI Core v0.5.

Input numbers must already have a reviewed source field mapping. Missing values
are errors; section family labels are never treated as numerical properties.
"""
from decimal import Decimal,InvalidOperation

def _d(v,field):
    try: d=Decimal(str(v))
    except (InvalidOperation,TypeError): raise ValueError("INVALID_"+field)
    if not d.is_finite(): raise ValueError("NONFINITE_"+field)
    return d

def material_si(*,E,G,nu,rho,stress_unit, density_unit):
    stress={"pa":Decimal(1),"kpa":Decimal(1000),"mpa":Decimal(1000000),
            "gpa":Decimal(1000000000),"psi":Decimal("6894.757293168"),
            "ksi":Decimal("6894757.293168")}
    densities={"kg/m3":Decimal(1),"t/m3":Decimal(1000),
               "lb/ft3":Decimal("16.01846337396014")}
    if stress_unit.casefold() not in stress: raise ValueError("UNSUPPORTED_STRESS_UNIT")
    if density_unit.casefold() not in densities: raise ValueError("UNSUPPORTED_DENSITY_UNIT")
    e=_d(E,"E")*stress[stress_unit.casefold()]
    g=_d(G,"G")*stress[stress_unit.casefold()]
    n=_d(nu,"NU")
    density=_d(rho,"RHO")*densities[density_unit.casefold()]
    if e<=0 or g<=0 or density<0 or not Decimal("-1")<n<Decimal("0.5"):
        raise ValueError("INVALID_MATERIAL_PROPERTIES")
    return {"E":str(e),"G":str(g),"nu":str(n),"rho":str(density),
            "units":{"E":"Pa","G":"Pa","rho":"kg/m3"}}

def section_si(*,A,Iy,Iz,J,length_unit):
    length={"m":Decimal(1),"mm":Decimal("0.001"),"cm":Decimal("0.01"),
            "in":Decimal("0.0254"),"ft":Decimal("0.3048")}
    if length_unit.casefold() not in length: raise ValueError("UNSUPPORTED_LENGTH_UNIT")
    k=length[length_unit.casefold()]
    vals={"A":_d(A,"A")*k**2,"Iy":_d(Iy,"IY")*k**4,
          "Iz":_d(Iz,"IZ")*k**4,"J":_d(J,"J")*k**4}
    if vals["A"]<=0 or any(vals[key]<0 for key in ("Iy","Iz","J")):
        raise ValueError("INVALID_SECTION_PROPERTIES")
    return {**{key:str(value) for key,value in vals.items()},
            "units":{"A":"m2","Iy":"m4","Iz":"m4","J":"m4"}}
