import unittest
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.staad_lexical import lex_staad
from linkoteq_importer.staad_geometry import extract_geometry
L=Limits(100000,1000,1000,10000,1000,10000,10000,100000)
def parse(s):
    a=archive_bytes(s.encode(),filename="sample.std",extension=".std",project_ref="p",namespace="n",policy_id="ret",limits=L)
    return extract_geometry(lex_staad(a,limits=L))
class GeometryTests(unittest.TestCase):
    def test_nodes_members_and_units(self):
        r=parse("STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 0 0 0; 2 5 0 0\nMEMBER INCIDENCES\n7 1 2\nFINISH\n")
        self.assertEqual(len(r.nodes),2);self.assertEqual(r.nodes[1].length_unit,"METER")
        self.assertEqual(r.members[0].source_id,7);self.assertEqual(r.diagnostics,())
    def test_units_change(self):
        r=parse("STAAD SPACE\nUNIT INCHES KIP\nJOINT COORDINATES\n1 1 2 3\nUNIT METER KN\n2 1 2 3\n")
        self.assertEqual([n.length_unit for n in r.nodes],["INCHES","METER"])
    def test_unknown_unit_is_not_assumed(self):
        r=parse("STAAD SPACE\nJOINT COORDINATES\n1 0 0 0\n")
        self.assertIsNone(r.nodes[0].length_unit);self.assertTrue(any("NODE_UNIT_UNKNOWN" in x for x in r.diagnostics))
    def test_missing_connectivity(self):
        r=parse("STAAD SPACE\nMEMBER INCIDENCES\n1 1 2\n")
        self.assertIn("MEMBER_MISSING_NODE:id=1",r.diagnostics)
    def test_duplicate_id(self):
        r=parse("STAAD SPACE\nJOINT COORDINATES\n1 0 0 0\n1 1 1 1\n")
        self.assertEqual(len(r.nodes),1);self.assertTrue(any("DUPLICATE" in x for x in r.diagnostics))
    def test_to_expression_not_interpreted(self):
        r=parse("STAAD SPACE\nMEMBER INCIDENCES\n1 TO 4 1 2\n")
        self.assertEqual(r.members,());self.assertTrue(any("UNSUPPORTED" in x for x in r.diagnostics))
    def test_nonfinite_rejected(self):
        r=parse("STAAD SPACE\nJOINT COORDINATES\n1 1e999 0 0\n")
        self.assertEqual(r.nodes,())
    def test_section_termination(self):
        r=parse("STAAD SPACE\nJOINT COORDINATES\n1 0 0 0\nSUPPORTS\n2 1 1 1\n")
        self.assertEqual(len(r.nodes),1)
    def test_zero_length_topology(self):
        r=parse("STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 0 0 0\nMEMBER INCIDENCES\n3 1 1\n")
        self.assertIn("MEMBER_ZERO_LENGTH_TOPOLOGY:id=3",r.diagnostics)
    def test_no_core_claim(self):
        self.assertEqual(parse("STAAD SPACE\n").core_mapping_status,"not-attempted")
