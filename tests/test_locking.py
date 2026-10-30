"""POSIX advisory ledger lock regression tests."""
import io
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from linkoteq_importer import ArchiveError, Limits, PhysicalSpan
from linkoteq_importer.durable import LocalArchiveStore

LIMITS = Limits(100, 100, 100, 100, 100, 1000, 10000, 10000)

class LedgerLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalArchiveStore(Path(self.temp.name))
        self.meta = self.store.ingest(io.BytesIO(b'1234'), filename='x.std', extension='.std',
                                      project_ref='a', namespace='n', policy_id='test', limits=LIMITS)

    def test_concurrent_revisions_unique(self):
        spans = (PhysicalSpan(0, 0, 4),)
        def commit(_):
            return self.store.commit_ledger(self.meta.object_id, project_ref='a',
                                            spans=spans, limits=LIMITS)
        with ThreadPoolExecutor(max_workers=8) as pool:
            revisions = list(pool.map(commit, range(20)))
        self.assertEqual(sorted(revisions), list(range(20)))
        for revision in revisions:
            self.assertEqual(self.store.read_ledger(self.meta.object_id, project_ref='a',
                                                    revision=revision)['revision'], revision)

    def test_invalid_revision_type(self):
        with self.assertRaisesRegex(ArchiveError, 'INVALID_LEDGER_REVISION'):
            self.store.read_ledger(self.meta.object_id, project_ref='a', revision=True)

    def test_reject_symlink_lock(self):
        folder = Path(self.temp.name) / self.meta.object_id
        (folder / '.ledger.lock').symlink_to(folder / 'source.bin')
        with self.assertRaisesRegex(ArchiveError, 'UNSAFE_LEDGER_LOCK'):
            self.store.commit_ledger(self.meta.object_id, project_ref='a',
                                     spans=(PhysicalSpan(0, 0, 4),), limits=LIMITS)

if __name__ == '__main__':
    unittest.main()
