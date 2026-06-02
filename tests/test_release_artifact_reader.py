import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.inspect_release_artifacts import inspect_release_artifacts


ROOT = Path(__file__).resolve().parents[1]


class ReleaseArtifactReaderTests(unittest.TestCase):
    def test_reader_summarizes_release_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifacts.json"
            path.write_text(json.dumps(_release_artifact()), encoding="utf-8")

            summary = inspect_release_artifacts(path)

        self.assertEqual(summary["schema"], "apc.release_artifacts_summary.v1")
        self.assertEqual(summary["source_schema"], "apc.release_artifacts.v1")
        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["tag"], "v0.1.0-test")
        self.assertEqual(summary["commit"], "a" * 40)
        self.assertEqual(summary["artifact_count"], 4)
        self.assertEqual(summary["fixture_count"], 2)
        self.assertEqual(summary["check_count"], 2)
        self.assertEqual(summary["failed_checks"], [])
        self.assertEqual(
            summary["artifact_schemas"]["handoff_fixture_listing"]["schema"],
            "apc.handoff_fixture_index.v1",
        )

    def test_reader_reports_failed_checks_without_claiming_release_quality(self):
        artifact = _release_artifact()
        artifact["status"] = "failed"
        artifact["checks"] = [
            {"name": "verifier_status", "ok": False},
            {"name": "docs_present", "ok": True},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifacts.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")

            summary = inspect_release_artifacts(path)

        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["failed_checks"], ["verifier_status"])
        self.assertIn("factual release evidence inspection", " ".join(summary["notes"]))
        self.assertNotIn("compatible", json.dumps(summary))

    def test_reader_rejects_unsupported_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifacts.json"
            path.write_text(json.dumps({"schema": "other.schema.v1"}), encoding="utf-8")

            summary = inspect_release_artifacts(path)

        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["reason"], "unsupported_schema")
        self.assertEqual(summary["source_schema"], "other.schema.v1")
        self.assertEqual(summary["artifact_count"], 0)

    def test_reader_marks_missing_file_failed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "missing.json"

            summary = inspect_release_artifacts(path)

        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["reason"], "missing_or_invalid_json")
        self.assertEqual(summary["fixture_count"], 0)

    def test_script_writes_summary_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            path = tmp / "artifacts.json"
            out = tmp / "summary.json"
            path.write_text(json.dumps(_release_artifact()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/inspect_release_artifacts.py",
                    str(path),
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
        self.assertEqual(stdout_report["schema"], "apc.release_artifacts_summary.v1")
        self.assertEqual(file_report["fixture_count"], 2)


def _release_artifact():
    return {
        "schema": "apc.release_artifacts.v1",
        "status": "ok",
        "tag": "v0.1.0-test",
        "commit": "a" * 40,
        "artifacts": {
            "verifier": {
                "exists": True,
                "schema": "apc.public_release_verification.v1",
                "payload": {"schema": "apc.public_release_verification.v1"},
            },
            "cpu_benchmark": {
                "exists": True,
                "schema": "apc.benchmark.v1",
                "payload": {"schema": "apc.benchmark.v1"},
            },
            "vector_demo_benchmark": {
                "exists": True,
                "schema": "apc.vector_demo_benchmark.v1",
                "payload": {"payload": {"benchmark": {"schema": "apc.vector_demo_benchmark.v1"}}},
            },
            "handoff_fixture_listing": {
                "exists": True,
                "schema": "apc.handoff_fixture_index.v1",
                "payload": {
                    "schema": "apc.handoff_fixture_index.v1",
                    "status": "ok",
                    "fixture_count": 2,
                },
            },
        },
        "checks": [
            {"name": "verifier_status", "ok": True},
            {"name": "handoff_fixture_listing_status", "ok": True},
        ],
    }


if __name__ == "__main__":
    unittest.main()
