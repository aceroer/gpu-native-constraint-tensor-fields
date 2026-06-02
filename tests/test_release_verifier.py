import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


import scripts.verify_public_release as verifier


ROOT = Path(__file__).resolve().parents[1]


class ReleaseVerifierTests(unittest.TestCase):
    def test_verifier_quick_mode_emits_json_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "verify.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/verify_public_release.py",
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            stdout_report = json.loads(completed.stdout)
            file_report = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(stdout_report["schema"], "apc.public_release_verification.v1")
        self.assertEqual(file_report["status"], "ok")
        self.assertEqual(file_report["mode"], "quick")
        self.assertIn("compileall", [check["name"] for check in file_report["checks"]])
        self.assertIn("vagent_handoff_consumer", [check["name"] for check in file_report["checks"]])
        self.assertIn("boundary_scan", [check["name"] for check in file_report["checks"]])

    def test_verifier_marks_failed_command(self):
        with mock.patch.object(verifier, "_checks") as checks:
            checks.return_value = [
                verifier.Check("bad", [sys.executable, "-c", "import sys; sys.exit(7)"])
            ]
            report = verifier.run_verification(full=False)

        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["checks"][0]["returncode"], 7)

    def test_verify_release_doc_mentions_full_mode(self):
        text = (ROOT / "docs" / "VERIFY_RELEASE.md").read_text(encoding="utf-8")

        self.assertIn("--full", text)
        self.assertIn("complete unittest suite", text)


if __name__ == "__main__":
    unittest.main()
