import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.inspect_benchmark_sweep import inspect_benchmark_sweep


ROOT = Path(__file__).resolve().parents[1]


class BenchmarkSweepReportTests(unittest.TestCase):
    def test_reader_summarizes_sweep_statuses_and_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sweep.json"
            path.write_text(json.dumps(_sweep_report()), encoding="utf-8")

            summary = inspect_benchmark_sweep(path)

        self.assertEqual(summary["schema"], "apc.benchmark_sweep_summary.v1")
        self.assertEqual(summary["source_schema"], "apc.benchmark_sweep.v1")
        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["name"], "binary_milp_smoke")
        self.assertEqual(summary["case_count"], 2)
        self.assertEqual(summary["unavailable_cases"], ["cuda_case"])
        self.assertEqual(summary["failed_cases"], [])
        self.assertEqual(summary["case_statuses"][0]["backend"], "cpu")
        self.assertEqual(summary["case_statuses"][0]["problem_family"], "binary_milp")
        self.assertEqual(summary["case_statuses"][0]["operator"], "repair_runtime")
        self.assertEqual(summary["case_statuses"][0]["out"], "/tmp/cpu.json")
        self.assertEqual(summary["case_statuses"][1]["backend_reason"], "nvcc not found")
        self.assertIn("kernel_time_s", summary["timing_fields"])

    def test_reader_keeps_cuda_unavailable_factual(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sweep.json"
            path.write_text(json.dumps(_sweep_report()), encoding="utf-8")

            summary = inspect_benchmark_sweep(path)

        cuda_case = summary["case_statuses"][1]

        self.assertEqual(cuda_case["status"], "unavailable")
        self.assertFalse(cuda_case["backend_available"])
        self.assertEqual(cuda_case["backend_reason"], "nvcc not found")

    def test_reader_rejects_unsupported_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sweep.json"
            path.write_text(json.dumps({"schema": "other.schema.v1"}), encoding="utf-8")

            summary = inspect_benchmark_sweep(path)

        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["reason"], "unsupported_schema")
        self.assertEqual(summary["source_schema"], "other.schema.v1")
        self.assertEqual(summary["case_count"], 0)

    def test_reader_marks_missing_file_failed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "missing.json"

            summary = inspect_benchmark_sweep(path)

        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["reason"], "missing_or_invalid_json")
        self.assertEqual(summary["case_statuses"], [])

    def test_script_writes_summary_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            path = tmp / "sweep.json"
            out = tmp / "summary.json"
            path.write_text(json.dumps(_sweep_report()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/inspect_benchmark_sweep.py",
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
        self.assertEqual(stdout_report["schema"], "apc.benchmark_sweep_summary.v1")
        self.assertEqual(file_report["unavailable_cases"], ["cuda_case"])
        self.assertNotIn("speedup", json.dumps(file_report).lower())


def _sweep_report():
    return {
        "schema": "apc.benchmark_sweep.v1",
        "status": "ok",
        "config_schema": "apc.benchmark_sweep_config.v1",
        "config_path": "benchmarks/sweeps/binary_milp_smoke.json",
        "name": "binary_milp_smoke",
        "case_count": 2,
        "cases": [
            {
                "name": "cpu_case",
                "status": "ok",
                "backend": "cpu",
                "problem_family": "binary_milp",
                "operator": "repair_runtime",
                "backend_available": True,
                "backend_reason": None,
                "spec": "examples/specs/binary_milp_tiny.json",
                "out": "/tmp/cpu.json",
                "report_schema": "apc.benchmark.v1",
                "timing": {
                    "kernel_time_s": 0.1,
                    "copy_time_s": 0.0,
                    "layout_conversion_time_s": 0.01,
                    "end_to_end_time_s": 0.12,
                },
            },
            {
                "name": "cuda_case",
                "status": "unavailable",
                "backend": "cuda",
                "problem_family": "binary_milp",
                "operator": "repair_runtime",
                "backend_available": False,
                "backend_reason": "nvcc not found",
                "spec": "examples/specs/binary_milp_tiny.json",
                "out": "/tmp/cuda.json",
                "report_schema": "apc.benchmark.v1",
                "timing": {
                    "kernel_time_s": 0.0,
                    "copy_time_s": 0.0,
                    "layout_conversion_time_s": 0.0,
                    "end_to_end_time_s": 0.0,
                },
            },
        ],
        "timing_fields": [
            "kernel_time_s",
            "copy_time_s",
            "layout_conversion_time_s",
            "end_to_end_time_s",
        ],
        "notes": [
            "Sweep configs define benchmark evidence inputs only.",
            "No performance claim is made without complete timing evidence.",
        ],
    }


if __name__ == "__main__":
    unittest.main()
