"""Known-answer SAP2000 field mapping; never confuse weight and mass density."""
from decimal import Decimal
from linkoteq_importer.sap2000_properties import CatalogEntry
from linkoteq_importer.sap2000_core_property_fields import source_material_to_si,source_section_to_si

def run():
    mat=CatalogEntry("S",(("E1","200"),("G12","80"),("U12","0.3"),
                          ("UnitMass","7850")),1)
    m=source_material_to_si(mat,stress_unit="GPa",density_unit="kg/m3")
    assert Decimal(m["E"])==200000000000 and Decimal(m["rho"])==7850
    sec=CatalogEntry("W",(("Area","1000"),("I22","1000000"),
                          ("I33","2000000"),("TorsConst","50000")),2)
    s=source_section_to_si(sec,length_unit="mm")
    assert Decimal(s["A"])==Decimal("0.001")
    assert Decimal(s["Iy"])==Decimal("0.000001")
    bad=CatalogEntry("S",(("E1","200"),("G12","80"),("U12","0.3"),
                          ("UnitWeight","77")),3)
    try:source_material_to_si(bad,stress_unit="GPa",density_unit="kg/m3")
    except ValueError as e:assert "WEIGHT_DENSITY" in str(e)
    else:raise AssertionError("weight density incorrectly treated as mass")
    print("PASS reviewed SAP2000 property field known answers; real file coverage not claimed")

if __name__=="__main__":run()
