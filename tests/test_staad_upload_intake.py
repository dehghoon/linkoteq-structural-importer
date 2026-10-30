from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from linkoteq_importer.durable import LocalArchiveStore
from linkoteq_importer.preservation import ArchiveError, Limits
from linkoteq_importer.staad_grid_companion import Upload
from linkoteq_importer.staad_upload_intake import ingest_staad_uploads
from linkoteq_importer.staad_grid_durable import read_staad_bundle

L = Limits(1000, 100, 100, 100, 100, 1000, 1000, 10000)

class IntakeTests(unittest.TestCase):
    def setUp(self):
        t = TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.store = LocalArchiveStore(Path(t.name))

    def run_intake(self, *files, **kwargs):
        return ingest_staad_uploads(self.store, files, project_ref='p',
                                    namespace='n', policy_id='ret', limits=L, **kwargs)

    def test_model_only(self):
        receipt = self.run_intake(Upload('a.std', b'STAAD SPACE'))
        self.assertIsNone(receipt.grid_object_id)
        self.assertEqual(receipt.grid_status, 'missing')

    def test_grid_auto(self):
        receipt = self.run_intake(Upload('A.SBK', b'STAAD SPACE'), Upload('a.GRD', b'\x00\xff'))
        self.assertIsNotNone(receipt.grid_object_id)
        self.assertEqual(read_staad_bundle(self.store, receipt.bundle_id, project_ref='p')['gridParsed'], 'not-attempted')

    def test_grid_explicit(self):
        receipt = self.run_intake(Upload('a.std', b'x'), Upload('other.grd', b'y'), selected_grid_filename='other.grd')
        self.assertEqual(read_staad_bundle(self.store, receipt.bundle_id, project_ref='p')['association'], 'explicit-selection')

    def test_unselected_different_name_rejected(self):
        with self.assertRaisesRegex(ArchiveError, 'EXPLICIT_GRID_SELECTION_REQUIRED'):
            self.run_intake(Upload('a.std', b'x'), Upload('other.grd', b'y'))
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_multiple_models_rejected(self):
        with self.assertRaisesRegex(ArchiveError, 'EXPECTED_ONE_STAAD_MODEL'):
            self.run_intake(Upload('a.std', b'x'), Upload('b.sbk', b'y'))

    def test_extra_file_rejected(self):
        with self.assertRaisesRegex(ArchiveError, 'UNSUPPORTED_UPLOAD_FILE'):
            self.run_intake(Upload('a.std', b'x'), Upload('notes.txt', b'y'))

    def test_multiple_grids_rejected(self):
        with self.assertRaisesRegex(ArchiveError, 'EXPECTED_AT_MOST_ONE_GRID'):
            self.run_intake(Upload('a.std', b'x'), Upload('a.grd', b'y'), Upload('b.grd', b'z'))

    def test_aggregate_limit_preflight(self):
        with self.assertRaisesRegex(ArchiveError, 'UPLOAD_SIZE_LIMIT'):
            self.run_intake(Upload('a.std', b'abc'), Upload('a.grd', b'def'), max_total_bytes=5)
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_no_files(self):
        with self.assertRaisesRegex(ArchiveError, 'NO_UPLOAD_FILES'):
            self.run_intake()

    def test_invalid_content(self):
        with self.assertRaisesRegex(ArchiveError, 'INVALID_UPLOAD'):
            self.run_intake(Upload('a.std', 'text'))
