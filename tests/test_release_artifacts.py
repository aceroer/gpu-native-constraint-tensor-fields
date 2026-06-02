import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.collect_release_artifacts import collect_release_artifacts


ROOT = Path(__file__).resolve().parents[1]


class ReleaseArtifactTests(unittest.TestCase):
    def test_collector_emits_json_ready_release_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verify = tmp / "verify.json"
            bench = tmp / "bench.json"
            vector = tmp / "vector.json"
            out = tmp / "artifacts.json"
            _write_fixture_artifacts(verify=verify, bench=bench, vector=vector)

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/collect_release_artifacts.py",
                    "--tag",
                    "v0.1.0-test",
                    "--verify",
                    str(verify),
                    "--bench",
                    str(bench),
                    "--vector-bench",
                    str(vector),
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

        self.assertEqual(stdout_report["schema"], "apc.release_artifacts.v1")
        self.assertEqual(file_report["status"], "ok")
        self.assertEqual(file_report["tag"], "v0.1.0-test")
        self.assertEqual(len(file_report["commit"]), 40)
        self.assertIn("verifier", file_report["artifacts"])
        self.assertIn("cpu_benchmark", file_report["artifacts"])
        self.assertIn("vector_demo_benchmark", file_report["artifacts"])
        self.assertIn("docs/TAG_PREP.md", [item["path"] for item in file_report["docs"]])
        self.assertIn("tests/test_tag_prep.py", [item["path"] for item in file_report["tests"]])

    def test_collector_marks_missing_artifact_failed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verify = tmp / "verify.json"
            bench = tmp / "bench.json"
            vector = tmp / "missing-vector.json"
            _write_fixture_artifacts(verify=verify, bench=bench, vector=tmp / "unused.json")
            vector.unlink(missing_ok=True)

            report = collect_release_artifacts(
                tag="v0.1.0-test",
                verify_path=verify,
                bench_path=bench,
                vector_bench_path=vector,
            )

        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["artifacts"]["vector_demo_benchmark"]["exists"])

    def test_release_artifacts_doc_names_contract(self):
        text = (ROOT / "docs" / "RELEASE_ARTIFACTS.md").read_text(encoding="utf-8")
        notes = (ROOT / "docs" / "RELEASE_NOTES_DRAFT.md").read_text(encoding="utf-8")

        self.assertIn("apc.release_artifacts.v1", text)
        self.assertIn("commit", text)
        self.assertIn("scripts/collect_release_artifacts.py", text)
        self.assertIn("release artifact contract", notes)


def _write_fixture_artifacts(*, verify: Path, bench: Path, vector: Path) -> None:
    verify.write_text(
        json.dumps(
            {
                "schema": "apc.public_release_verification.v1",
                "status": "ok",
                "mode": "quick",
                "checks": [],
            }
        ),
        encoding="utf-8",
    )
    bench.write_text(
        json.dumps(
            {
                "schema": "apc.benchmark.v1",
                "metrics": {},
                "notes": [],
            }
        ),
        encoding="utf-8",
    )
    vector.write_text(
        json.dumps(
            {
                "payload": {
                    "benchmark": {
                        "schema": "apc.vector_demo_benchmark.v1",
                    }
                }
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
