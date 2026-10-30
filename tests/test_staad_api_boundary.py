from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from linkoteq_importer.durable import LocalArchiveStore
from linkoteq_importer.preservation import ArchiveError, Limits
from linkoteq_importer.staad_grid_companion import Upload
from linkoteq_importer.staad_api_boundary import (AuthenticatedPrincipal, StaadUploadRequest, accept_authorized_staad_upload)

L = Limits(1000, 100, 100, 100, 100, 1000, 1000, 10000)

class BoundaryTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = LocalArchiveStore(Path(tmp.name))
        self.request = StaadUploadRequest('p1', 'n', 'ret', (Upload('a.std', b'STAAD SPACE'), Upload('a.grd', b'grid')))

    def call(self, principal=None, authorize=None, request=None):
        return accept_authorized_staad_upload(self.store, principal if principal is not None else AuthenticatedPrincipal('u1'),
            request if request is not None else self.request, authorize_project_write=authorize if authorize is not None else lambda p, r: True,
            limits=L, max_total_bytes=1000)

    def test_authorized_model_and_grid(self):
        receipt = self.call()
        self.assertIsNotNone(receipt.grid_object_id)
        self.assertEqual(receipt.grid_parsed, 'not-attempted')

    def test_denied_does_not_write(self):
        with self.assertRaisesRegex(ArchiveError, 'PROJECT_ACCESS_DENIED'):
            self.call(authorize=lambda p, r: False)
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_missing_principal_does_not_write(self):
        with self.assertRaisesRegex(ArchiveError, 'UNAUTHENTICATED'):
            self.call(principal=AuthenticatedPrincipal(''))
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_authorizer_sees_server_principal_and_requested_project(self):
        observed = []
        self.call(authorize=lambda principal, project: observed.append((principal.subject_id, project)) or True)
        self.assertEqual(observed, [('u1', 'p1')])

    def test_reject_over_limit_before_write(self):
        oversized = StaadUploadRequest('p1', 'n', 'ret', (Upload('a.std', b'x' * 1001),))
        with self.assertRaisesRegex(ArchiveError, 'UPLOAD_SIZE_LIMIT'):
            self.call(request=oversized)
        self.assertEqual(list(self.store.root.iterdir()), [])
