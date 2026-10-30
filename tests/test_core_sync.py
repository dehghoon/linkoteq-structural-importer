import tempfile
import unittest
from pathlib import Path
from linkoteq_importer.core_sync import snapshot_core, assess_core_change, CoreSyncError

SHA='a'*40
class CoreSyncTests(unittest.TestCase):
    def make_core(self, root):
        (root/'typescript').mkdir()
        (root/'CORE_CONTRACT.md').write_text('# Linkoteq Structural Core Contract v0.5\n')
        (root/'AI_GPT_UPDATE_POLICY.md').write_text('policy')
        (root/'typescript/index.ts').write_text('\n'.join(f'export interface {x} {{}}' for x in ('StructuralModel','Section','Material','Diaphragm','Member','Surface','CalculatorEnvelope','CalculatorWriteback')))
    def test_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.make_core(root)
            s=snapshot_core(root,commit=SHA)
            self.assertEqual(assess_core_change(s,s)['activation'],'unchanged')
    def test_drift_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.make_core(root)
            old=snapshot_core(root,commit=SHA)
            (root/'typescript/index.ts').write_text((root/'typescript/index.ts').read_text()+'\nexport interface Joist {}')
            new=snapshot_core(root,commit='b'*40)
            report=assess_core_change(old,new)
            self.assertTrue(report['requires_review'])
            self.assertIn('Joist',report['added_types'])
            self.assertEqual(report['activation'],'blocked')
    def test_missing_type(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.make_core(root)
            (root/'typescript/index.ts').write_text('export interface Section {}')
            with self.assertRaises(CoreSyncError):snapshot_core(root,commit=SHA)
    def test_unpinned_commit(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.make_core(root)
            with self.assertRaises(CoreSyncError):snapshot_core(root,commit='main')
if __name__=='__main__':unittest.main()
