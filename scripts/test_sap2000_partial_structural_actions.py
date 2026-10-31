"""Regression: boundaries and loads attach without dropping partial members."""
from decimal import Decimal
from linkoteq_importer.sap2000_geometry import GeometryView,Joint,Frame
from linkoteq_importer.sap2000_properties import PropertyView
from linkoteq_importer.sap2000_boundary import BoundaryView,JointRestraint,JointSpring,FrameRelease
from linkoteq_importer.sap2000_loads import LoadView,LoadPattern,JointForce
from linkoteq_importer.partial_structural_actions import build_partial_model_with_actions

def run():
    g=GeometryView((Joint("1",Decimal(0),Decimal(0),Decimal(0),1),
                    Joint("2",Decimal(1),Decimal(0),Decimal(0),2)),
                   (Frame("10","1","2",3),),"hash","KN, m, C",())
    p=PropertyView((),(),(),(),(),"hash")
    b=BoundaryView((JointRestraint("1",(True,True,True,False,False,False),4),),
                   (JointSpring("2","Local",(Decimal(1),)*6,5),),
                   (FrameRelease("10",(True,)+(False,)*11,6),),(),"hash")
    l=LoadView((LoadPattern("D","Dead",Decimal(1),7),),
               (JointForce("2","D","Global",(Decimal(1),)*6,8),),(),"hash")
    model=build_partial_model_with_actions(g,p,b,l,stress_unit="kPa",
                                           density_unit="kg/m3",length_unit="m")
    assert len(model["members"])==1 and model["members"][0]["mappingStatus"]=="partial"
    assert len(model["restraints"])==len(model["sourceSprings"])==1
    assert len(model["sourceFrameReleases"])==len(model["sourceJointForces"])==1
    assert model["sourceSprings"][0]["sourceCoordinateSystem"]=="Local"
    assert not model["analysisReady"] and not model["mapped_to_core"]
    print("PASS partial model retains boundary and load source values")

if __name__=="__main__":run()
