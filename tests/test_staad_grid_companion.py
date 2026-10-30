import unittest
from linkoteq_importer.preservation import ArchiveError, Limits
from linkoteq_importer.staad_grid_companion import Upload, attach_grid

L = Limits(1000, 100, 100, 100, 100, 1000, 1000, 10000)

def attach(model="frame.std", companions=(), selected=None):
    return attach_grid(Upload(model, b"STAAD SPACE\n"), tuple(companions),
                       project_ref="project", namespace="namespace", policy_id="retention",
                       limits=L, selected_filename=selected)

class GridCompanionTests(unittest.TestCase):
    def test_std_matching(self):
        r=attach(companions=[Upload("FRAME.GRD", b"\x00grid\xff")])
        self.assertEqual(r.archive.retrieve(),b"\x00grid\xff")
        self.assertEqual(r.association,"filename-match")
        self.assertEqual(r.report()["stages"]["parsed"],"not-attempted")
    def test_sbk_matching(self):
        self.assertIsNotNone(attach("frame.sbk",[Upload("frame.grd",b"a")]))
    def test_missing_is_not_inferred(self):
        self.assertIsNone(attach())
    def test_unrelated_not_associated(self):
        self.assertIsNone(attach(companions=[Upload("other.grd",b"a")]))
    def test_explicit_selection(self):
        r=attach(companions=[Upload("other.grd",b"a")],selected="other.grd")
        self.assertEqual(r.association,"explicit-selection")
    def test_ambiguous(self):
        with self.assertRaisesRegex(ArchiveError,"AMBIGUOUS"):
            attach(companions=[Upload("frame.grd",b"a"),Upload("FRAME.GrD",b"b")])
    def test_duplicate_filename(self):
        with self.assertRaisesRegex(ArchiveError,"DUPLICATE"):
            attach(companions=[Upload("a.grd",b"a"),Upload("a.grd",b"b")])
    def test_path_traversal(self):
        with self.assertRaisesRegex(ArchiveError,"UNSAFE"):
            attach(companions=[Upload("../frame.grd",b"a")])
    def test_windows_path(self):
        with self.assertRaisesRegex(ArchiveError,"UNSAFE"):
            attach(companions=[Upload("folder\\frame.grd",b"a")])
    def test_oversize(self):
        with self.assertRaisesRegex(ArchiveError,"MAX_BYTES"):
            attach(companions=[Upload("frame.grd",b"a"*1001)])
    def test_invalid_extension(self):
        with self.assertRaisesRegex(ArchiveError,"NON_GRID"):
            attach(companions=[Upload("frame.txt",b"a")])
    def test_selected_not_found(self):
        with self.assertRaisesRegex(ArchiveError,"SELECTED_GRID_NOT_FOUND"):
            attach(selected="other.grd")
    def test_model_type(self):
        with self.assertRaisesRegex(ArchiveError,"NOT_STAAD_MODEL"):
            attach("frame.s2k")
    def test_model_size_limit(self):
        with self.assertRaisesRegex(ArchiveError,"MAX_BYTES"):
            attach_grid(Upload("frame.std",b"a"*1001),(),project_ref="p",namespace="n",policy_id="ret",limits=L)
    def test_fidelity_never_claims_core_mapping(self):
        r=attach(companions=[Upload("frame.grd",b"grid")])
        self.assertEqual(r.report()["stages"]["mapped"],"not-attempted")
        self.assertEqual(r.report()["gridOrigin"],"source-companion-unparsed")
