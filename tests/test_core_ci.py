import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_core.py"

class CoreCITests(unittest.TestCase):
    def test_script_requires_arguments(self):
        p = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--core", p.stderr)

    def test_script_has_no_auto_promotion(self):
        text = SCRIPT.read_text()
        self.assertIn("requires_review", text)
        self.assertIn('exit_code = 2 if report["requires_review"] else 0', text)

    def test_workflow_is_read_only(self):
        workflow = (SCRIPT.parents[1] / ".github/workflows/core-compatibility.yml").read_text()
        self.assertIn("contents: read", workflow)
        self.assertNotIn("pull-requests: write", workflow)
        self.assertIn("LINKOTEQ_APPROVED_CORE_COMMIT", workflow)

if __name__ == "__main__":
    unittest.main()
