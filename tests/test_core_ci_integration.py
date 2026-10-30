"""End-to-end tests using an isolated synthetic Git repository; no network."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/check_core.py'
EXPORTS = ('StructuralModel', 'Section', 'Material', 'Diaphragm', 'Member',
           'Surface', 'CalculatorEnvelope', 'CalculatorWriteback')

class CoreCIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.env = dict(os.environ, GIT_AUTHOR_NAME='Test', GIT_AUTHOR_EMAIL='test@example.org',
                        GIT_COMMITTER_NAME='Test', GIT_COMMITTER_EMAIL='test@example.org')
        (self.root/'typescript').mkdir()
        (self.root/'CORE_CONTRACT.md').write_text('# Linkoteq Structural Core Contract v0.5\n')
        (self.root/'AI_GPT_UPDATE_POLICY.md').write_text('policy v1\n')
        (self.root/'typescript/index.ts').write_text(''.join('export interface '+x+' {}\n' for x in EXPORTS))
        self.baseline = self.commit()

    def commit(self):
        subprocess.run(['git','-C',str(self.root),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.root),'commit','-qm','fixture'],check=True,env=self.env)
        return subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip()

    def check(self, baseline, candidate):
        output = self.root/'result.json'
        result = subprocess.run([sys.executable,str(SCRIPT),'--core',str(self.root),
                                 '--baseline',baseline,'--candidate',candidate,'--output',str(output)],
                                capture_output=True,text=True,env=dict(os.environ,PYTHONPATH=str(SCRIPT.parents[1]/'src')))
        return result.returncode,json.loads(output.read_text())

    def test_same_commit_no_drift(self):
        code, report = self.check(self.baseline,self.baseline)
        self.assertEqual(code,0)
        self.assertEqual(report['activation'],'unchanged')

    def test_changed_policy_requires_review(self):
        (self.root/'AI_GPT_UPDATE_POLICY.md').write_text('policy v2\n')
        candidate=self.commit()
        code, report=self.check(self.baseline,candidate)
        self.assertEqual(code,2)
        self.assertEqual(report['changed_files'],['AI_GPT_UPDATE_POLICY.md'])
        self.assertEqual(report['activation'],'blocked')

    def test_missing_commit_fails_closed_and_writes_report(self):
        code,report=self.check(self.baseline,'0'*40)
        self.assertEqual(code,3)
        self.assertEqual(report['activation'],'blocked')
        self.assertEqual(report['status'],'error')

    def test_incomplete_sha_fails_closed(self):
        code,report=self.check(self.baseline,self.baseline[:8])
        self.assertEqual(code,3)
        self.assertEqual(report['activation'],'blocked')

    def test_missing_required_type_fails_closed(self):
        (self.root/'typescript/index.ts').write_text('export interface Section {}\n')
        candidate=self.commit()
        code,report=self.check(self.baseline,candidate)
        self.assertEqual(code,3)
        self.assertEqual(report['activation'],'blocked')

if __name__ == '__main__': unittest.main()
