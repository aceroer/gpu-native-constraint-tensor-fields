import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import smoke_release_evidence


ROOT = Path(__file__).resolve().parents[1]


class ReleaseEvidenceSmokeTests(unittest.TestCase):
    def test_smoke_command_runs_release_evidence_route(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            out = tmp / "smoke.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/smoke_release_evidence.py",
                    "--tag",
                    "v0.1.0-test",
                    "--output-dir",
                    str(tmp),
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            stdout_report = json.loads(completed.stdout)
            file_report = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(stdout_report["schema"], "apc.release_evidence_smoke.v1")
        self.assertEqual(file_report["status"], "ok")
        self.assertEqual(file_report["tag"], "v0.1.0-test")
        self.assertEqual([step["name"] for step in file_report["steps"]], ["verifier", "collector", "reader"])
        self.assertTrue(file_report["paths"]["verifier"].endswith("apc-release-verify.json"))
        self.assertTrue(file_report["paths"]["collector"].endswith("apc-release-artifacts.json"))
        self.assertTrue(file_report["paths"]["reader"].endswith("apc-release-artifacts-summary.json"))
        for step in file_report["steps"]:
            self.assertEqual(step["returncode"], 0)
            self.assertTrue(step["output_exists"])

    def test_smoke_report_is_factual_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report = smoke_release_evidence.run_release_evidence_smoke(
                tag="v0.1.0-test",
                output_dir=Path(tmpdir),
            )

        text = json.dumps(report)
        self.assertIn("factual release evidence steps only", text)
        self.assertNotIn("compatible", text)

    def test_smoke_stops_after_failed_verifier(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            def fake_run(*args, **kwargs):
                return subprocess.CompletedProcess(args=args[0], returncode=1, stdout="", stderr="failed")

            with mock.patch.object(smoke_release_evidence.subprocess, "run", side_effect=fake_run):
                report = smoke_release_evidence.run_release_evidence_smoke(
                    tag="v0.1.0-test",
                    output_dir=output_dir,
                )

        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["steps"][0]["name"], "verifier")
        self.assertEqual(report["steps"][0]["returncode"], 1)
        self.assertTrue(report["steps"][1]["skipped"])
        self.assertTrue(report["steps"][2]["skipped"])


if __name__ == "__main__":
    unittest.main()
