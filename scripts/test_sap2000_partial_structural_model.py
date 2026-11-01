"""Regression: missing section/material never blocks partial model construction."""
from dataclasses import replace
from linkoteq_importer.sap2000_geometry import GeometryView,Joint,Frame
from linkoteq_importer.sap2000_properties import PropertyView,CatalogEntry,FrameSectionAssignment
from linkoteq_importer.partial_structural_model import build_partial_model
from decimal import Decimal

def run():
    g=GeometryView((Joint("1",Decimal(0),Decimal(0),Decimal(0),1),
                    Joint("2",Decimal(1),Decimal(0),Decimal(0),2)),
                   (Frame("10","1","2",3),Frame("11","1","2",4)),"hash","KN, m, C",())
    p=PropertyView((CatalogEntry("S",(("Material","S"),),1),),
                   (CatalogEntry("W",(("Material","S"),("Area","1"),
                                       ("I22","1"),("I33","1"),("TorsConst","1")),2),),
                   (FrameSectionAssignment("10","W",None,3),
                    FrameSectionAssignment("11","None",None,4)),
                   (CatalogEntry("S",(("E1","200"),("G12","80"),
                                       ("U12","0.3"),("UnitMass","7850")),5),),
                   (),"hash")
    result=build_partial_model(g,p,stress_unit="GPa",density_unit="kg/m3",length_unit="m")
    assert len(result["members"])==2 and len(result["nodes"])==2
    assert result["members"][0]["mappingStatus"]=="property-values-mapped"
    assert result["members"][1]["mappingStatus"]=="partial"
    assert result["members"][1]["diagnostics"][0].startswith("UNKNOWN_SECTION:")
    assert not result["analysisReady"] and not result["mapped_to_core"]
    print("PASS partial model preserves unresolved members without inventing properties")

if __name__=="__main__":run()
