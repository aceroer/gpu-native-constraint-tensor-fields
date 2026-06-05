import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from apc.run_artifacts import write_run_artifacts
from apc.runtime_qubo_cpu import QUBORuntimeConfig, describe_qubo_cpu_reference_execution_from_json


ROOT = Path(__file__).resolve().parents[1]
TINY_QUBO = ROOT / "examples" / "specs" / "qubo_tiny.json"


class RunArtifactTests(unittest.TestCase):
    def test_writer_creates_stable_run_directory_layout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report = describe_qubo_cpu_reference_execution_from_json(
                TINY_QUBO,
                config=QUBORuntimeConfig(max_iters=2),
            )
            manifest = write_run_artifacts(
                report=report,
                source_spec=TINY_QUBO,
                artifact_dir=tmpdir,
                run_id="tiny_qubo",
            )
            run_dir = Path(tmpdir) / "tiny_qubo"

            self.assertEqual(manifest["schema"], "apc.run_artifacts.v1")
            self.assertEqual(manifest["problem_family"], "qubo")
            self.assertTrue((run_dir / "input.json").exists())
            self.assertTrue((run_dir / "result.json").exists())
            self.assertTrue((run_dir / "ledger.json").exists())
            self.assertTrue((run_dir / "timings.json").exists())
            self.assertTrue((run_dir / "metadata.json").exists())

    def test_writer_keeps_public_artifacts_json_ready_and_sanitized(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report = {
                "schema": "example.runtime.v1",
                "status": "implemented",
                "problem_family": "qubo",
                "backend": "cpu",
                "source_path": str(TINY_QUBO),
                "evidence": {"runtime_report": str(Path(tmpdir) / "report.json")},
                "ledger": [{"iteration": 0, "energy": 0.0}],
            }
            write_run_artifacts(
                report=report,
                source_spec=TINY_QUBO,
                artifact_dir=tmpdir,
                run_id="sanitized",
            )
            run_dir = Path(tmpdir) / "sanitized"
            result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
            metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
            timings = json.loads((run_dir / "timings.json").read_text(encoding="utf-8"))

            self.assertEqual(result["source_path"], "qubo_tiny.json")
            self.assertEqual(result["evidence"]["runtime_report"], "report.json")
            self.assertNotIn(tmpdir, json.dumps(result))
            self.assertEqual(metadata["source_spec_name"], "qubo_tiny.json")
            self.assertEqual(timings["schema"], "apc.run_artifact_timings.v1")
            self.assertIn("kernel_time_s", timings["timing"])

    def test_cli_can_write_run_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / "artifacts"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "apc.cli",
                    "run",
                    str(TINY_QUBO),
                    "--family",
                    "auto",
                    "--max-iters",
                    "2",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--run-id",
                    "cli_qubo",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            run_dir = artifact_dir / "cli_qubo"
            self.assertEqual(report["run_artifacts"]["schema"], "apc.run_artifacts.v1")
            self.assertTrue((run_dir / "metadata.json").exists())
            self.assertTrue((run_dir / "result.json").exists())


if __name__ == "__main__":
    unittest.main()
