"""Independent known-answer checks for SAP global load-vector projection.

These assertions do not require a solver and explicitly test signed force
conversion, zero transverse components and gravity deferral.
"""
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from linkoteq_importer.sap2000_global_load_vectors import project_global_distributed_vectors

def load(frame, direction, a, b, *, system="GLOBAL", kind="Force"):
    return SimpleNamespace(frame_id=frame, pattern_id="DEAD", source_line=12,
        direction=direction, coordinate_system=system, load_type=kind,
        distance_type="RelDist", start=Decimal("0"), end=Decimal("1"),
        magnitude_start=Decimal(a), magnitude_end=Decimal(b))

def run():
    archive = SimpleNamespace(sourceHash="known-answer")
    geometry = SimpleNamespace(source_hash="known-answer")
    records = [
        load("Y1", "Y", "-2.5", "-4"),
        load("Z1", "Z", "3", "0"),
        load("G1", "Gravity", "1", "2"),
        load("L1", "Y", "5", "6", system="Local"),
        load("M1", "Z", "1", "2", kind="Moment"),
    ]
    with patch("linkoteq_importer.sap2000_global_load_vectors.audit_sap2000_load_units",
               return_value={"distinctDeclarations": ["KN, m, C"], "issues": []}), \
         patch("linkoteq_importer.sap2000_global_load_vectors.extract_advanced_loads",
               return_value=SimpleNamespace(distributed=records)):
        result = project_global_distributed_vectors(archive, geometry)
    assert len(result["vectorCandidates"]) == 2
    assert len(result["deferredLoads"]) == 3
    y, z = result["vectorCandidates"]
    assert y["startVectorNPerM"] == ["0", "-2500.0", "0"]
    assert y["endVectorNPerM"] == ["0", "-4000", "0"]
    assert z["startVectorNPerM"] == ["0", "0", "3000"]
    assert z["endVectorNPerM"] == ["0", "0", "0"]
    assert not result["gravitySignVerified"] and not result["mappedToCore"]
    print("PASS SAP_GLOBAL_VECTOR_KNOWN_ANSWERS")

if __name__ == "__main__":
    run()
