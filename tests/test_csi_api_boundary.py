"""CSI preservation boundary tests; no vendor parsing is claimed."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from linkoteq_importer.csi_api_boundary import CsiUploadRequest, preserve_authorized_csi_upload
from linkoteq_importer.durable import LocalArchiveStore
from linkoteq_importer.preservation import ArchiveError, Limits
from linkoteq_importer.staad_api_boundary import AuthenticatedPrincipal

L = Limits(1000, 100, 100, 100, 100, 1000, 1000, 10000)


class CsiBoundaryTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.store = LocalArchiveStore(Path(temp.name))
        self.principal = AuthenticatedPrincipal('user-1')

    def submit(self, filename='model.$et', content=b'\xff\x00\r\nUNKNOWN', allowed=True):
        return preserve_authorized_csi_upload(
            self.store, self.principal,
            CsiUploadRequest('project-1', 'ns', 'retention', filename, content),
            authorize_project_write=lambda principal, project: allowed,
            limits=L,
        )

    def test_exact_bytes_and_stage_gates(self):
        raw = b'\xff\x00\r\nUNKNOWN'
        receipt = self.submit(content=raw)
        self.assertEqual(self.store.retrieve(receipt.object_id, project_ref='project-1'), raw)
        self.assertEqual(receipt.source_hash, sha256(raw).hexdigest())
        self.assertEqual((receipt.parsed, receipt.mapped, receipt.grid_parsed),
                         ('not-attempted',) * 3)

    def test_accepted_extensions(self):
        for filename in ('a.e2k', 'a.$et', 'a.s2k', 'a.$2k', 'a.E2K'):
            with self.subTest(filename=filename):
                self.assertEqual(self.submit(filename=filename).preserved, 'succeeded')

    def test_denied_has_no_side_effects(self):
        with self.assertRaisesRegex(ArchiveError, 'PROJECT_ACCESS_DENIED'):
            self.submit(allowed=False)
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_over_limit_has_no_side_effects(self):
        with self.assertRaisesRegex(ArchiveError, 'UPLOAD_SIZE_LIMIT'):
            self.submit(content=b'a' * 1001)
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_reject_unsupported_and_unsafe_names(self):
        for filename in ('a.pdf', '../a.e2k', 'dir/a.s2k', 'dir\\a.s2k'):
            with self.subTest(filename=filename):
                with self.assertRaises(ArchiveError):
                    self.submit(filename=filename)
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_cross_project_retrieval_is_denied(self):
        receipt = self.submit()
        with self.assertRaisesRegex(ArchiveError, 'ARCHIVE_NOT_FOUND'):
            self.store.retrieve(receipt.object_id, project_ref='another-project')

    def test_zero_bytes_preserved(self):
        receipt = self.submit(content=b'')
        self.assertEqual(receipt.byte_length, 0)
        self.assertEqual(self.store.retrieve(receipt.object_id, project_ref='project-1'), b'')


if __name__ == '__main__':
    unittest.main()
