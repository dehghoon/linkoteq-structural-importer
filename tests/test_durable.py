import io
from pathlib import Path
import tempfile
import unittest

from linkoteq_importer import ArchiveError, Limits, PhysicalSpan
from linkoteq_importer.durable import LocalArchiveStore

LIMITS = Limits(1024, 100, 100, 1024, 100, 1000, 10000, 4096)


class DurableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalArchiveStore(Path(self.temp.name))

    def ingest(self, data, **kwargs):
        return self.store.ingest(io.BytesIO(data), filename='model.std', extension='.std',
                                 project_ref='tenant-a', namespace='model-a',
                                 policy_id='test', limits=LIMITS, **kwargs)

    def test_roundtrip_binary(self):
        for data in (b'', b'\x00\xff', b'\xef\xbb\xbf\r\n', b'x'*1024):
            meta = self.ingest(data)
            self.assertEqual(self.store.retrieve(meta.object_id, project_ref='tenant-a'), data)

    def test_boundary_cleanup(self):
        with self.assertRaisesRegex(ArchiveError, 'MAX_BYTES_EXCEEDED'):
            self.ingest(b'x'*1025)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_cancel_cleanup(self):
        with self.assertRaisesRegex(ArchiveError, 'CANCELLED'):
            self.ingest(b'hello', cancelled=lambda: True)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_project_isolation(self):
        meta = self.ingest(b'hello')
        with self.assertRaisesRegex(ArchiveError, 'ARCHIVE_NOT_FOUND'):
            self.store.retrieve(meta.object_id, project_ref='tenant-b')

    def test_tamper_detection(self):
        meta = self.ingest(b'hello')
        (Path(self.temp.name) / meta.object_id / 'source.bin').write_bytes(b'HELLO')
        with self.assertRaisesRegex(ArchiveError, 'HASH_MISMATCH'):
            self.store.retrieve(meta.object_id, project_ref='tenant-a')

    def test_ledger_revisions(self):
        meta = self.ingest(b'abcd')
        spans = (PhysicalSpan(0, 0, 2), PhysicalSpan(1, 2, 4))
        self.assertEqual(self.store.commit_ledger(meta.object_id, project_ref='tenant-a', spans=spans, limits=LIMITS), 0)
        self.assertEqual(self.store.commit_ledger(meta.object_id, project_ref='tenant-a', spans=spans, limits=LIMITS), 1)
        with self.assertRaisesRegex(ArchiveError, 'INVALID_SPAN_COVERAGE'):
            self.store.commit_ledger(meta.object_id, project_ref='tenant-a', spans=(PhysicalSpan(0, 0, 3),), limits=LIMITS)


if __name__ == '__main__':
    unittest.main()
