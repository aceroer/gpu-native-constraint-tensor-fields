import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from apc import BenchmarkConfig, run_cuda_benchmark_report


ROOT = Path(__file__).resolve().parents[2]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"


class CUDABenchReportTests(unittest.TestCase):
    def test_cuda_report_uses_benchmark_schema(self):
        report = run_cuda_benchmark_report(
            TINY_SPEC,
            BenchmarkConfig(backend="cuda", max_iters=2),
            element_count=16,
        )

        self.assertEqual(report["schema"], "apc.benchmark.v1")
        self.assertEqual(report["backend"]["name"], "cuda")
        self.assertIn("kernel_time_s", report["metrics"])
        self.assertIn("copy_time_s", report["metrics"])
        self.assertNotIn("speedup", report)

    def test_cuda_report_is_unavailable_without_nvcc_or_device(self):
        report = run_cuda_benchmark_report(TINY_SPEC, BenchmarkConfig(backend="cuda"), element_count=16)

        if report["backend"]["available"]:
            self.assertGreaterEqual(report["metrics"]["kernel_time_s"], 0.0)
            self.assertGreaterEqual(report["metrics"]["copy_time_s"], 0.0)
        else:
            self.assertIn("reason", report["backend"])
            self.assertEqual(report["metrics"]["kernel_time_s"], 0.0)
            self.assertEqual(report["metrics"]["copy_time_s"], 0.0)

    def test_run_cuda_bench_script_writes_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "cuda.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_cuda_bench.py",
                    str(TINY_SPEC),
                    "--out",
                    str(output),
                    "--element-count",
                    "16",
                    "--cuda-arch",
                    "sm_89",
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
        self.assertEqual(file_payload["backend"]["name"], "cuda")
        self.assertIn("cuda_arch", file_payload["config"])


if __name__ == "__main__":
    unittest.main()
