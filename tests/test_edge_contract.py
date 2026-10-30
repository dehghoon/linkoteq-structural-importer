import io
from pathlib import Path
import tempfile
import unittest
from linkoteq_importer import ArchiveError, Limits, PhysicalSpan
from linkoteq_importer.durable import LocalArchiveStore

L = Limits(8, 8, 8, 8, 8, 1000, 1000, 128)

class EdgeContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalArchiveStore(Path(self.temp.name))

    def ingest(self, data):
        return self.store.ingest(io.BytesIO(data), filename='f.std', extension='.std',
            project_ref='p', namespace='n', policy_id='policy', limits=L)

    def test_limit_exact_and_over(self):
        self.assertEqual(self.store.retrieve(self.ingest(b'12345678').object_id, project_ref='p'), b'12345678')
        with self.assertRaisesRegex(ArchiveError, 'MAX_BYTES_EXCEEDED'):
            self.ingest(b'123456789')

    def test_ledger_read_and_tamper(self):
        meta = self.ingest(b'abcd')
        self.store.commit_ledger(meta.object_id, project_ref='p',
            spans=(PhysicalSpan(0,0,4),), limits=L)
        self.assertEqual(self.store.read_ledger(meta.object_id, project_ref='p', revision=0)['revision'], 0)
        path = Path(self.temp.name)/meta.object_id/'ledger-0.json'
        path.write_text('{"revision":0,"sourceHash":"bad","spans":[]}', encoding='utf-8')
        with self.assertRaisesRegex(ArchiveError, 'LEDGER_INTEGRITY_ERROR'):
            self.store.read_ledger(meta.object_id, project_ref='p', revision=0)

    def test_missing_ledger(self):
        meta = self.ingest(b'')
        with self.assertRaisesRegex(ArchiveError, 'LEDGER_NOT_FOUND'):
            self.store.read_ledger(meta.object_id, project_ref='p', revision=0)

    def test_project_denied_ledger(self):
        meta = self.ingest(b'ab')
        with self.assertRaisesRegex(ArchiveError, 'ARCHIVE_NOT_FOUND'):
            self.store.read_ledger(meta.object_id, project_ref='wrong', revision=0)

if __name__ == '__main__':
    unittest.main()
