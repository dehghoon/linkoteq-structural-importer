"""Known-answer property reference binding at Core v0.5 boundary."""
from decimal import Decimal
from linkoteq_importer.sap2000_geometry import GeometryView,Joint,Frame
from linkoteq_importer.sap2000_properties import PropertyView,CatalogEntry,FrameSectionAssignment
from linkoteq_importer.core_property_references import bind_property_references

def run():
    geometry=GeometryView(
        (Joint("1",Decimal(0),Decimal(0),Decimal(0),1),
         Joint("2",Decimal(1),Decimal(0),Decimal(0),2)),
        (Frame("F","1","2",3),),"hash","KN_m_C",())
    materials=(CatalogEntry("Steel",(("material","Steel"),),4),
               CatalogEntry("Other",(("material","Other"),),5))
    sections=(CatalogEntry("W1",(("sectionname","W1"),("material","Steel")),6),)
    def props(assignments,hash="hash"):
        return PropertyView(materials,sections,assignments,(),(),hash)
    a=FrameSectionAssignment("F","W1",None,7)
    out=bind_property_references(geometry,props((a,)))
    m=out["members"][0]
    assert m["sectionId"]=="sap2000:section:W1"
    assert m["materialId"]=="sap2000:material:Steel"
    assert out["mapped_to_core"] is False
    assert out["unmappedRequiredMemberFields"]
    override=FrameSectionAssignment("F","W1","Other",7)
    assert bind_property_references(geometry,props((override,)))["members"][0]["materialId"]=="sap2000:material:Other"
    assert bind_property_references(geometry,props(()))["unresolvedReferences"]==["MISSING_SECTION_ASSIGNMENT:F"]
    try: bind_property_references(geometry,props((a,a)))
    except ValueError as e: assert "AMBIGUOUS" in str(e)
    else: raise AssertionError("duplicate assignment accepted")
    try: bind_property_references(geometry,props((a,),"different"))
    except ValueError as e: assert "SOURCE_HASH_MISMATCH" in str(e)
    else: raise AssertionError("cross-source mapping accepted")
    print("PASS Core property reference identity binding; NOT complete Core model")

if __name__=="__main__": run()
