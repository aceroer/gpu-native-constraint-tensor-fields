import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"


class VectorDemoBenchmarkTests(unittest.TestCase):
    def test_vector_demo_benchmark_script_writes_projected_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "vector_demo_bench.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_vector_demo_bench.py",
                    str(TINY_SPEC),
                    "--out",
                    str(output),
                    "--batch-size",
                    "3",
                    "--top-k",
                    "2",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(output.exists())
            stdout_payload = json.loads(completed.stdout)
            file_payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(stdout_payload["projection"]["kind"], "runtime_summary")
        self.assertEqual(file_payload["projection"]["kind"], "runtime_summary")
        self.assertEqual(file_payload["payload"]["metrics"]["branch_count"], 9)
        self.assertEqual(file_payload["payload"]["metrics"]["selected_action_count"], 2)

    def test_report_includes_runtime_path_metrics_and_timing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "vector_demo_bench.json"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/run_vector_demo_bench.py",
                    str(TINY_SPEC),
                    "--out",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            report = json.loads(output.read_text(encoding="utf-8"))

        benchmark = report["payload"]["benchmark"]
        timing = benchmark["timing"]
        self.assertIn("StatePool", benchmark["runtime_path"])
        self.assertIn("ReductionGate", benchmark["runtime_path"])
        self.assertGreaterEqual(timing["end_to_end_time_s"], timing["kernel_time_s"])
        self.assertEqual(timing["copy_time_s"], 0.0)

    def test_no_speedup_claim_without_copy_time_accounting(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "vector_demo_bench.json"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/run_vector_demo_bench.py",
                    str(TINY_SPEC),
                    "--out",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            report = json.loads(output.read_text(encoding="utf-8"))

        notes = " ".join(report["payload"]["benchmark"]["notes"])
        self.assertIn("No speedup claim", notes)
        self.assertNotIn("speedup ratio", json.dumps(report).lower())


if __name__ == "__main__":
    unittest.main()
