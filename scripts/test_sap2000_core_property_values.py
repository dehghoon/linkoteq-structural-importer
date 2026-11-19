"""Independent SI known answers for dimensional property conversion."""
from decimal import Decimal
from linkoteq_importer.core_property_values import material_si,section_si

def run():
    m=material_si(E="200",G="80",nu="0.3",rho="7850",
                  stress_unit="GPa",density_unit="kg/m3")
    assert Decimal(m["E"])==Decimal("200000000000")
    assert Decimal(m["G"])==Decimal("80000000000")
    assert Decimal(m["rho"])==Decimal("7850")
    s=section_si(A="1000",Iy="1000000",Iz="2000000",J="50000",length_unit="mm")
    assert Decimal(s["A"])==Decimal("0.001")
    assert Decimal(s["Iy"])==Decimal("0.000001")
    assert Decimal(s["Iz"])==Decimal("0.000002")
    assert Decimal(s["J"])==Decimal("0.00000005")
    for call in (lambda:section_si(A="1",Iy="1",Iz="1",J="1",length_unit="unknown"),
                 lambda:material_si(E="200",G="80",nu="0.3",rho="7850",
                                    stress_unit="GPa",density_unit="kN/m3"),
                 lambda:section_si(A="0",Iy="1",Iz="1",J="1",length_unit="mm")):
        try:call()
        except ValueError:pass
        else:raise AssertionError("unsupported dimensional data accepted")
    print("PASS SI property conversion known answers; source field adapter not yet implemented")

if __name__=="__main__":run()
