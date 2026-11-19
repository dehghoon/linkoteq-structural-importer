from base64 import b64decode
from fastapi.testclient import TestClient
from linkoteq_importer.gpt3_upload_api import app

SOURCE = b'''TABLE: "PROGRAM CONTROL"
ProgramName=SAP2000 Version=19.0.0 CurrUnits="KN, m, C"
TABLE: "JOINT COORDINATES"
Joint=1 CoordSys=GLOBAL CoordType=Cartesian XorR=0 Y=0 Z=0
Joint=2 CoordSys=GLOBAL CoordType=Cartesian XorR=2 Y=0 Z=0
Joint=3 CoordSys=GLOBAL CoordType=Cartesian XorR=2 Y=2 Z=0
Joint=4 CoordSys=GLOBAL CoordType=Cartesian XorR=0 Y=2 Z=0
TABLE: "CONNECTIVITY - AREA"
Area=A1 NumJoints=4 Joint1=1 Joint2=2 Joint3=3 Joint4=4
END TABLE DATA
'''


def test_upload_api_keeps_source_and_area_geometry(monkeypatch):
    monkeypatch.setenv("SAP2000_IMPORTER_API_TOKEN", "synthetic-local-test-token")
    client = TestClient(app)
    assert client.get("/health").json()["areasSupported"] is True
    response = client.post("/api/import/sap2000",
        headers={"Authorization": "Bearer synthetic-local-test-token"},
        data={"project_id": "synthetic"},
        files={"file": ("synthetic.s2k", SOURCE, "text/plain")})
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["geometryPreview"]["nodes"]) == 4
    assert len(body["geometryPreview"]["areas"]) == 1
    assert body["analysisReady"] is False
    assert b64decode(body["sourceArchive"]["bytesBase64"]) == SOURCE


def test_upload_api_rejects_unauthorized_source_upload(monkeypatch):
    monkeypatch.setenv("SAP2000_IMPORTER_API_TOKEN", "synthetic-local-test-token")
    response = TestClient(app).post("/api/import/sap2000", data={"project_id": "synthetic"},
        files={"file": ("synthetic.s2k", SOURCE, "text/plain")})
    assert response.status_code == 401
