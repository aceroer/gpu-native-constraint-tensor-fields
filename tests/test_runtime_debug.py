import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from apc.debug import inspect_runtime_debug


ROOT = Path(__file__).resolve().parents[1]
TINY_QUBO = ROOT / "examples" / "specs" / "qubo_tiny.json"


class RuntimeDebugTests(unittest.TestCase):
    def test_debug_report_inspects_spec_ctir_layout_status_and_cuda(self):
        report = inspect_runtime_debug(spec=TINY_QUBO, batch_size=4)

        self.assertEqual(report["schema"], "apc.runtime_debug_report.v1")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["spec"]["name"], "qubo_tiny.json")
        self.assertEqual(report["spec"]["problem_family"], "qubo")
        self.assertIn("domain", report["ctir"])
        self.assertIn("views", report["layout"])
        self.assertEqual(report["ledger"]["status"], "not_requested")
        self.assertEqual(report["run_artifacts"]["status"], "not_requested")
        self.assertEqual(report["status_codes"]["schema"], "apc.runtime_status_codes.v1")
        self.assertIn("nvcc_available", report["cuda"])
        self.assertIn("device_available", report["cuda"])
        self.assertIn("driver_version", report["cuda"])
        self.assertIn("driver_model", report["cuda"])
        self.assertIn("selected_arch", report["cuda"])
        self.assertIn("skip_reason", report["cuda"])
        checkpoint = report["beta_checkpoint"]
        self.assertEqual(checkpoint["schema"], "apc.runtime_debug_beta_checkpoint.v1")
        self.assertIn(
            checkpoint["compute_mode"],
            {"tcc", "wddm", "headless_cuda_or_driver_default", "cuda_unavailable"},
        )
        self.assertIn(checkpoint["host_role"], {"compute_core", "orchestration_layer"})
        self.assertIn("host_compiler_readiness", checkpoint)
        self.assertIn("cuda_differential_test_status", checkpoint)
        self.assertEqual(checkpoint["release_artifact_status"]["status"], "not_requested")
        self.assertEqual(checkpoint["pci_hal_boundary_status"]["cpu_hardware_contract"], "PCI/PCIe enumeration")

    def test_debug_report_reads_ledger_and_run_artifacts_without_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / "artifacts"
            run = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "apc.cli",
                    "run",
                    str(TINY_QUBO),
                    "--family",
                    "auto",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--run-id",
                    "debug_qubo",
                    "--ledger-out",
                    str(Path(tmpdir) / "qubo-ledger.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            report = inspect_runtime_debug(
                spec=TINY_QUBO,
                ledger=Path(tmpdir) / "qubo-ledger.json",
                artifact_dir=artifact_dir / "debug_qubo",
            )

            encoded = json.dumps(report, sort_keys=True)

        self.assertEqual(report["ledger"]["status"], "ok")
        self.assertEqual(report["run_artifacts"]["status"], "ok")
        self.assertIn("metadata.json", report["run_artifacts"]["files"])
        self.assertNotIn(tmpdir, encoded)

    def test_script_writes_debug_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "debug.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/inspect_runtime_debug.py",
                    str(TINY_QUBO),
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

        self.assertEqual(stdout_report["schema"], "apc.runtime_debug_report.v1")
        self.assertEqual(file_report["status"], "ok")

    def test_script_reads_release_artifact_status_into_beta_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "release-artifacts.json"
            artifact.write_text(
                json.dumps({"schema": "apc.release_artifacts.v1", "status": "ok"}) + "\n",
                encoding="utf-8",
            )
            out = Path(tmpdir) / "debug.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/inspect_runtime_debug.py",
                    str(TINY_QUBO),
                    "--release-artifacts",
                    str(artifact),
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(out.read_text(encoding="utf-8"))

        release_status = report["beta_checkpoint"]["release_artifact_status"]
        self.assertEqual(release_status["status"], "ok")
        self.assertEqual(release_status["schema"], "apc.release_artifacts.v1")
        self.assertEqual(release_status["name"], "release-artifacts.json")

    def test_debug_doc_names_version_checkpoint(self):
        text = (ROOT / "docs" / "DEBUGGING.md").read_text(encoding="utf-8")

        self.assertIn("apc.runtime_debug_report.v1", text)
        self.assertIn("lowered CTIR", text)
        self.assertIn("run artifacts", text)
        self.assertIn("runtime status codes", text)
        self.assertIn("nvcc_available", text)
        self.assertIn("apc.runtime_debug_beta_checkpoint.v1", text)
        self.assertIn("compute_mode", text)
        self.assertIn("host_compiler_readiness", text)
        self.assertIn("pci_hal_boundary_status", text)
        self.assertIn("Every version after 0.4", text)
        self.assertNotIn("speedup", text.lower())


if __name__ == "__main__":
    unittest.main()
