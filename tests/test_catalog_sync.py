import hashlib
import json
import unittest
from linkoteq_importer.catalog_sync import verify_catalog, CatalogSyncError

SHA = "a" * 40
def fixture(records, family="sections", commit=SHA, rev=1):
    data = json.dumps({"core_commit": commit, "catalog_name": family, "schema_revision": rev, "records": records}).encode()
    return data, hashlib.sha256(data).hexdigest()

def section(id="joist-1"):
    return {"id": id, "name": "Sample Joist", "analysis": {k: {"value": 1.0, "unit": "mm2" if k == "A" else "mm4"} for k in ("A", "Iy", "Iz", "J")}}

class CatalogSyncTests(unittest.TestCase):
    def check(self, records, family="sections"):
        data, digest = fixture(records, family)
        return verify_catalog(data, core_commit=SHA, expected_sha256=digest, catalog_name=family, approved_schema_revision=1)

    def test_valid_joist_section(self):
        self.assertEqual(self.check([section()]).record_ids, ("joist-1",))

    def test_duplicate_id_rejected(self):
        with self.assertRaises(CatalogSyncError): self.check([section(), section()])

    def test_missing_units_rejected(self):
        s = section(); s["analysis"]["A"].pop("unit")
        with self.assertRaises(CatalogSyncError): self.check([s])

    def test_nonfinite_rejected(self):
        s = section(); s["analysis"]["J"]["value"] = float("nan")
        with self.assertRaises(CatalogSyncError): self.check([s])

    def test_digest_mismatch_rejected(self):
        data, digest = fixture([section()])
        with self.assertRaises(CatalogSyncError): verify_catalog(data, core_commit=SHA, expected_sha256="0" * 64, catalog_name="sections", approved_schema_revision=1)

    def test_core_commit_mismatch_rejected(self):
        data, digest = fixture([section()])
        with self.assertRaises(CatalogSyncError): verify_catalog(data, core_commit="b" * 40, expected_sha256=digest, catalog_name="sections", approved_schema_revision=1)

    def test_unknown_schema_rejected(self):
        data, digest = fixture([section()], rev=2)
        with self.assertRaises(CatalogSyncError): verify_catalog(data, core_commit=SHA, expected_sha256=digest, catalog_name="sections", approved_schema_revision=2)

    def test_valid_material(self):
        analysis = {k: {"value": 1, "unit": "MPa" if k in ("E", "G") else "kg/m3"} for k in ("E", "G", "rho")}
        analysis["nu"] = 0.3
        result = self.check([{"id":"steel", "name":"Steel", "type":"steel", "analysis":analysis}], "materials")
        self.assertEqual(result.catalog_name, "materials")

    def test_empty_rejected(self):
        with self.assertRaises(CatalogSyncError): self.check([])

    def test_byte_limit_rejected(self):
        data, digest = fixture([section()])
        with self.assertRaises(CatalogSyncError): verify_catalog(data, core_commit=SHA, expected_sha256=digest, catalog_name="sections", approved_schema_revision=1, max_bytes=1)
