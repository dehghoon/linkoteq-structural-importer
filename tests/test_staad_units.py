import unittest
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.staad_lexical import lex_staad
from linkoteq_importer.staad_geometry import extract_geometry
from linkoteq_importer.staad_units import normalize_geometry

L = Limits(100000, 1000, 1000, 10000, 1000, 10000, 10000, 100000)
def convert(source):
    archive = archive_bytes(source.encode(), filename="fixture.std", extension=".std",
        project_ref="p", namespace="n", policy_id="ret", limits=L)
    return normalize_geometry(extract_geometry(lex_staad(archive, limits=L)))

class UnitTests(unittest.TestCase):
    def test_meters(self):
        r=convert("STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 0 0 0; 2 3 4 0\nMEMBER INCIDENCES\n9 1 2\n")
        self.assertEqual(r.members[0].length_m,5.0)
    def test_inches(self):
        r=convert("STAAD SPACE\nUNIT INCHES KIP\nJOINT COORDINATES\n1 12 0 0\n")
        self.assertAlmostEqual(r.nodes[0].xyz_m[0],.3048)
    def test_feet(self):
        r=convert("STAAD SPACE\nUNIT FEET KIP\nJOINT COORDINATES\n1 1 0 0\n")
        self.assertAlmostEqual(r.nodes[0].xyz_m[0],.3048)
    def test_millimeters(self):
        r=convert("STAAD SPACE\nUNIT MM KN\nJOINT COORDINATES\n1 1000 0 0\n")
        self.assertEqual(r.nodes[0].xyz_m[0],1)
    def test_centimeters(self):
        r=convert("STAAD SPACE\nUNIT CM KN\nJOINT COORDINATES\n1 100 0 0\n")
        self.assertEqual(r.nodes[0].xyz_m[0],1)
    def test_mixed_units(self):
        r=convert("STAAD SPACE\nUNIT INCHES KIP\nJOINT COORDINATES\n1 0 0 0\nUNIT METER KN\n2 1 0 0\nMEMBER INCIDENCES\n5 1 2\n")
        self.assertEqual(r.members[0].length_m,1)
    def test_no_default(self):
        r=convert("STAAD SPACE\nJOINT COORDINATES\n1 0 0 0\n")
        self.assertEqual(r.nodes,());self.assertIn("NODE_UNIT_NOT_CONVERTIBLE:id=1",r.diagnostics)
    def test_missing_node_blocks_member(self):
        r=convert("STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 0 0 0\nMEMBER INCIDENCES\n3 1 2\n")
        self.assertEqual(r.members,());self.assertIn("MEMBER_NORMALIZATION_BLOCKED:id=3",r.diagnostics)
    def test_zero_length_blocks_member(self):
        r=convert("STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 0 0 0; 2 0 0 0\nMEMBER INCIDENCES\n3 1 2\n")
        self.assertEqual(r.members,());self.assertIn("MEMBER_LENGTH_INVALID:id=3",r.diagnostics)
    def test_provenance_retained(self):
        r=convert("STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 1 2 3\n")
        self.assertEqual(r.nodes[0].source_line,4);self.assertGreater(r.nodes[0].source_byte,0)
    def test_core_mapping_not_claimed(self):
        r=convert("STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 1 2 3\n")
        self.assertEqual(r.mapping_status,"not-attempted")
    def test_nonfinite_overflow_rejected(self):
        r=convert("STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 1e308 0 0; 2 -1e308 0 0\nMEMBER INCIDENCES\n3 1 2\n")
        self.assertEqual(r.members,());self.assertIn("MEMBER_LENGTH_INVALID:id=3",r.diagnostics)
