import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from apc import BenchmarkConfig, run_benchmark, write_benchmark_report


ROOT = Path(__file__).resolve().parents[1]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"


class BenchmarkTests(unittest.TestCase):
    def test_cpu_benchmark_output_is_json_ready(self):
        report = run_benchmark(
            TINY_SPEC,
            BenchmarkConfig(backend="cpu", max_iters=4, batch_size=4, seed=0),
        )
        encoded = json.dumps(report, sort_keys=True)
        payload = json.loads(encoded)

        self.assertEqual(payload["schema"], "apc.benchmark.v1")
        self.assertEqual(payload["backend"]["name"], "cpu")
        self.assertTrue(payload["backend"]["available"])
        self.assertEqual(payload["metrics"]["best_penalty"], 0.0)
        self.assertIn("violation_decay", payload["metrics"])
        self.assertGreaterEqual(payload["metrics"]["end_to_end_time_s"], payload["metrics"]["kernel_time_s"])
        self.assertIn("copy-time accounting", " ".join(payload["notes"]))

    def test_report_can_be_written_to_file(self):
        report = run_benchmark(TINY_SPEC, BenchmarkConfig(max_iters=2))
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bench.json"
            write_benchmark_report(report, path)
            loaded = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(loaded["schema"], "apc.benchmark.v1")
        self.assertTrue(loaded["ledger"])

    def test_cuda_backend_is_reported_separately(self):
        report = run_benchmark(TINY_SPEC, BenchmarkConfig(backend="cuda"))

        self.assertEqual(report["backend"]["name"], "cuda")
        self.assertFalse(report["backend"]["available"])
        self.assertEqual(report["metrics"]["copy_time_s"], 0.0)
        self.assertIn("No GPU speedup", " ".join(report["notes"]))

    def test_run_bench_script_writes_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "latest.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_bench.py",
                    str(TINY_SPEC),
                    "--out",
                    str(output),
                    "--max-iters",
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

        self.assertEqual(stdout_payload["schema"], "apc.benchmark.v1")
        self.assertEqual(file_payload["schema"], "apc.benchmark.v1")


if __name__ == "__main__":
    unittest.main()
