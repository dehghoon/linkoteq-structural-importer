import hashlib
import unittest

from linkoteq_importer import (Limits, ArchiveError, PhysicalSpan, archive_bytes,
                               entity_id, validate_spans, fidelity_report)

LIMITS = Limits(1024, 100, 100, 1024, 100, 1000, 1000, 4096)


class PreservationTests(unittest.TestCase):
    def archive(self, data=b'\x00\xff\r\n'):
        return archive_bytes(data, filename='sample.sbk', extension='.sbk',
                             project_ref='p1', namespace='n1', policy_id='test', limits=LIMITS)

    def test_exact_bytes(self):
        for raw in (b'', b'\xff', b'\xef\xbb\xbf\r\n', b'\n\r\n', b'\x00' * 10):
            a = self.archive(raw)
            self.assertEqual(a.retrieve(), raw)
            self.assertEqual(a.sourceHash, hashlib.sha256(raw).hexdigest())

    def test_boundary(self):
        self.archive(b'x' * 1024)
        with self.assertRaisesRegex(ArchiveError, 'MAX_BYTES_EXCEEDED'):
            self.archive(b'x' * 1025)

    def test_limits(self):
        with self.assertRaises(ArchiveError):
            Limits(0, 1, 1, 1, 1, 1, 1, 1)
        with self.assertRaises(ArchiveError):
            Limits(True, 1, 1, 1, 1, 1, 1, 1)

    def test_spans(self):
        a = self.archive()
        ledger = validate_spans(a, (PhysicalSpan(0, 0, 2), PhysicalSpan(1, 2, 4)), limits=LIMITS)
        self.assertEqual(ledger.sourceHash, a.sourceHash)
        for bad in ((PhysicalSpan(0, 0, 3),), (PhysicalSpan(0, 1, 4),),
                    (PhysicalSpan(0, 0, 2), PhysicalSpan(1, 1, 4))):
            with self.assertRaises(ArchiveError):
                validate_spans(a, bad, limits=LIMITS)
        self.assertEqual(validate_spans(self.archive(b''), (), limits=LIMITS).spans, ())

    def test_identity(self):
        a = entity_id('ns', 'STAAD', 'member', '001', 'scope')
        self.assertEqual(a, entity_id('ns', 'STAAD', 'member', '001', 'scope'))
        self.assertNotEqual(a, entity_id('ns', 'STAAD', 'member', '1', 'scope'))
        self.assertNotEqual(a, entity_id('ns', 'STAAD', 'member', '001', 'other'))
        self.assertNotEqual(a, entity_id('ns', 'STAAD', 'node', '001', 'scope'))

    def test_report(self):
        stages = fidelity_report(self.archive())['stages']
        self.assertEqual(stages['preserved'], 'succeeded')
        self.assertTrue(all(v == 'not-attempted' for k, v in stages.items() if k != 'preserved'))

    def test_integrity(self):
        from dataclasses import replace
        a = self.archive()
        with self.assertRaisesRegex(ArchiveError, 'HASH_MISMATCH'):
            replace(a, sourceBytes=b'xxxx').retrieve()


if __name__ == '__main__':
    unittest.main()
