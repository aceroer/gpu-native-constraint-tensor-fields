import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.run_benchmark_sweep import run_benchmark_sweep


ROOT = Path(__file__).resolve().parents[1]


class BenchmarkSweepRunnerTests(unittest.TestCase):
    def test_runner_consumes_config_and_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _write_temp_config(tmp)
            summary_path = tmp / "summary.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_benchmark_sweep.py",
                    str(config),
                    "--out",
                    str(summary_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            stdout_summary = json.loads(completed.stdout)
            file_summary = json.loads(summary_path.read_text(encoding="utf-8"))
            cpu_report_exists = (tmp / "cpu.json").exists()
            cuda_report_exists = (tmp / "cuda.json").exists()

        self.assertEqual(stdout_summary["schema"], "apc.benchmark_sweep.v1")
        self.assertEqual(file_summary["status"], "ok")
        self.assertEqual(file_summary["case_count"], 2)
        self.assertEqual([case["name"] for case in file_summary["cases"]], ["cpu_case", "cuda_case"])
        self.assertEqual(file_summary["cases"][0]["status"], "ok")
        self.assertIn(file_summary["cases"][1]["status"], {"ok", "unavailable"})
        self.assertTrue(cpu_report_exists)
        self.assertTrue(cuda_report_exists)

    def test_runner_summary_is_json_ready(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            summary = run_benchmark_sweep(_write_temp_config(tmp))

        encoded = json.dumps(summary, sort_keys=True)

        self.assertIn("apc.benchmark_sweep.v1", encoded)
        self.assertIn("kernel_time_s", encoded)
        self.assertNotIn("speedup", encoded.lower())

    def test_runner_handles_qubo_and_maxsat_sweeps(self):
        summaries = [
            run_benchmark_sweep(ROOT / "benchmarks" / "sweeps" / "qubo_smoke.json"),
            run_benchmark_sweep(ROOT / "benchmarks" / "sweeps" / "maxsat_smoke.json"),
        ]

        for summary in summaries:
            with self.subTest(name=summary["name"]):
                self.assertEqual(summary["schema"], "apc.benchmark_sweep.v1")
                self.assertEqual(summary["status"], "ok")
                self.assertEqual(summary["case_count"], 2)
                families = {case["problem_family"] for case in summary["cases"]}
                self.assertEqual(len(families), 1)
                self.assertIn(next(iter(families)), {"qubo", "maxsat"})
                self.assertEqual(summary["cases"][0]["status"], "ok")
                self.assertIn(summary["cases"][1]["status"], {"ok", "unavailable"})
                self.assertIn("operator", summary["cases"][0])
                self.assertIn("operator", summary["cases"][1])
                if summary["cases"][1]["status"] == "unavailable":
                    self.assertIsNotNone(summary["cases"][1]["backend_reason"])
                self.assertIn("kernel_time_s", summary["cases"][0]["timing"])

    def test_runner_keeps_cuda_unavailable_factual(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            summary = run_benchmark_sweep(_write_temp_config(tmp))

        cuda_case = next(case for case in summary["cases"] if case["backend"] == "cuda")

        self.assertEqual(cuda_case["operator"], "repair_runtime")
        if cuda_case["status"] == "unavailable":
            self.assertFalse(cuda_case["backend_available"])
            self.assertIsNotNone(cuda_case["backend_reason"])
        else:
            self.assertTrue(cuda_case["backend_available"])

    def test_runner_rejects_bad_config_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            bad = tmp / "bad.json"
            bad.write_text(json.dumps({"schema": "wrong"}), encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, "scripts/run_benchmark_sweep.py", str(bad)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unsupported benchmark sweep config schema", completed.stderr)


def _write_temp_config(tmp: Path) -> Path:
    config = tmp / "sweep.json"
    config.write_text(
        json.dumps(
            {
                "schema": "apc.benchmark_sweep_config.v1",
                "name": "temp_smoke",
                "cases": [
                    {
                        "name": "cpu_case",
                        "spec": "examples/specs/binary_milp_tiny.json",
                        "backend": "cpu",
                        "out": str(tmp / "cpu.json"),
                        "max_iters": 2,
                        "batch_size": 4,
                        "seed": 0,
                        "penalty_weight": 10.0,
                    },
                    {
                        "name": "cuda_case",
                        "spec": "examples/specs/binary_milp_tiny.json",
                        "backend": "cuda",
                        "out": str(tmp / "cuda.json"),
                        "max_iters": 2,
                        "batch_size": 4,
                        "seed": 0,
                        "penalty_weight": 10.0,
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
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return config


if __name__ == "__main__":
    unittest.main()
