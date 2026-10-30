import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from linkoteq_importer.durable import LocalArchiveStore
from linkoteq_importer.preservation import ArchiveError, Limits
from linkoteq_importer.staad_grid_companion import Upload
from linkoteq_importer.staad_grid_durable import ingest_staad_bundle, read_staad_bundle

L = Limits(1000, 100, 100, 100, 100, 1000, 1000, 10000)

class DurableGridTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalArchiveStore(Path(self.temp.name))

    def ingest(self, companions=(), model=None, selected=None):
        return ingest_staad_bundle(self.store, model or Upload('frame.sbk', b'STAAD SPACE\n'),
            tuple(companions), project_ref='p', namespace='n', policy_id='ret',
            limits=L, selected_filename=selected)

    def test_roundtrip_binary_grid(self):
        bundle = self.ingest([Upload('FRAME.GRD', b'\x00\xffabc')])
        self.assertEqual(self.store.retrieve(bundle.grid.object_id, project_ref='p'), b'\x00\xffabc')
        r = read_staad_bundle(self.store, bundle.bundle_id, project_ref='p')
        self.assertEqual(r['gridParsed'], 'not-attempted')
        self.assertEqual(r['association'], 'filename-match')

    def test_missing_grid(self):
        bundle = self.ingest()
        self.assertIsNone(bundle.grid)
        self.assertEqual(read_staad_bundle(self.store, bundle.bundle_id, project_ref='p')['gridStatus'], 'missing')

    def test_explicit_selection(self):
        bundle = self.ingest([Upload('other.grd', b'custom')], selected='other.grd')
        self.assertEqual(bundle.association, 'explicit-selection')

    def test_unauthorized_read(self):
        bundle = self.ingest()
        with self.assertRaisesRegex(ArchiveError, 'BUNDLE_NOT_FOUND'):
            read_staad_bundle(self.store, bundle.bundle_id, project_ref='other')

    def test_invalid_companion_does_not_ingest(self):
        with self.assertRaisesRegex(ArchiveError, 'NON_GRID_COMPANION'):
            self.ingest([Upload('bad.txt', b'hi')])
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_ambiguous_does_not_ingest(self):
        with self.assertRaisesRegex(ArchiveError, 'AMBIGUOUS_GRID_COMPANION'):
            self.ingest([Upload('FRAME.grd', b'a'), Upload('frame.grd', b'b')])
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_tampered_grid_detected(self):
        bundle = self.ingest([Upload('frame.grd', b'grid')])
        (self.store.root / bundle.grid.object_id / 'source.bin').write_bytes(b'xxxx')
        with self.assertRaisesRegex(ArchiveError, 'HASH_MISMATCH'):
            read_staad_bundle(self.store, bundle.bundle_id, project_ref='p')

    def test_tampered_bundle_detected(self):
        bundle = self.ingest([Upload('frame.grd', b'grid')])
        path = self.store.root / 'staad-bundles' / (bundle.bundle_id + '.json')
        record = json.loads(path.read_text())
        record['gridSourceHash'] = '0'*64
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ArchiveError, 'BUNDLE_INTEGRITY_ERROR'):
            read_staad_bundle(self.store, bundle.bundle_id, project_ref='p')

    def test_invalid_bundle_id(self):
        with self.assertRaisesRegex(ArchiveError, 'INVALID_BUNDLE_ID'):
            read_staad_bundle(self.store, '../bad', project_ref='p')
