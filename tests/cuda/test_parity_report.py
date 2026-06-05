import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.inspect_cuda_parity import inspect_cuda_parity


ROOT = Path(__file__).resolve().parents[2]
PARITY_DOC = ROOT / "docs" / "CUDA_OPERATOR_PARITY.md"


class CUDAParityReportTests(unittest.TestCase):
    def test_report_names_targets_reference_routes_and_status(self):
        report = inspect_cuda_parity(PARITY_DOC)

        self.assertEqual(report["schema"], "apc.cuda_parity_report.v1")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["backend"], "cuda")
        self.assertGreaterEqual(report["target_count"], 3)
        target_ids = {target["target_id"] for target in report["targets"]}
        self.assertIn("qubo_energy_eval", target_ids)
        self.assertIn("qubo_bitflip_score", target_ids)
        self.assertIn("maxsat_clause_eval", target_ids)
        for target in report["targets"]:
            self.assertEqual(target["backend"], "cuda")
            self.assertIn("reference_route", target)
            self.assertIn("status", target)
            self.assertIn("timing_fields", target)

    def test_report_keeps_unavailable_cuda_explicit(self):
        report = inspect_cuda_parity(PARITY_DOC)
        env = report["cuda_environment"]

        self.assertIn("nvcc_available", env)
        self.assertIn("device_available", env)
        self.assertIn("selected_arch", env)
        self.assertIn("skip_reason", env)
        if env["availability"] == "unavailable":
            self.assertIsNotNone(env["skip_reason"])
            unavailable = [target for target in report["targets"] if target["status"] == "unavailable"]
            self.assertTrue(unavailable)

    def test_report_docs_keep_boundary_and_timing_fields_visible(self):
        text = PARITY_DOC.read_text(encoding="utf-8")

        self.assertIn("apc.cuda_parity_report.v1", text)
        self.assertIn("operator, family, backend, reference route, and status", text)
        self.assertIn("Unavailable CUDA is recorded as unavailable", text)
        self.assertIn("kernel_time_s", text)
        self.assertIn("copy_time_s", text)
        self.assertNotIn("speedup", text.lower())

    def test_script_writes_cuda_parity_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "cuda-parity.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/inspect_cuda_parity.py",
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

        self.assertEqual(stdout_report["schema"], "apc.cuda_parity_report.v1")
        self.assertEqual(file_report["target_count"], stdout_report["target_count"])


if __name__ == "__main__":
    unittest.main()
