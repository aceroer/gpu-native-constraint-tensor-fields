import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"
TINY_QUBO = ROOT / "examples" / "specs" / "qubo_tiny.json"
TINY_MAXSAT = ROOT / "examples" / "specs" / "maxsat_tiny.json"


class CLITests(unittest.TestCase):
    def test_validate_accepts_valid_spec(self):
        completed = _run_cli("validate", str(TINY_SPEC))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["n_vars"], 3)
        self.assertEqual(payload["linear_rows"], 3)

    def test_validate_exits_nonzero_on_invalid_spec(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid = Path(tmpdir) / "invalid.json"
            invalid.write_text('{"domain": {"type": "integer"}}\n', encoding="utf-8")
            completed = _run_cli("validate", str(invalid))

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("error:", completed.stderr)

    def test_inspect_ctir_prints_compact_summary(self):
        completed = _run_cli("inspect-ctir", str(TINY_SPEC), "--batch-size", "6")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["domain"]["n_vars"], 3)
        self.assertEqual(payload["constraints"]["linear_rows"], 3)
        self.assertEqual(payload["moves"]["batch_size"], 6)

    def test_run_writes_ledger_and_reports_best_candidate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "runs" / "latest" / "ledger.json"
            completed = _run_cli(
                "run",
                str(TINY_SPEC),
                "--backend",
                "cpu",
                "--ledger-out",
                str(ledger_path),
                "--max-iters",
                "4",
                "--batch-size",
                "4",
                "--seed",
                "0",
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "apc.runtime_family_route.v1")
            self.assertEqual(report["problem_family"], "binary_milp")
            self.assertEqual(report["backend"], "cpu")
            self.assertEqual(report["status"], "ok")
            self.assertTrue(report["feasible"])
            self.assertEqual(report["best_penalty"], 0.0)
            self.assertIn("evidence", report)
            self.assertTrue(ledger_path.exists())

            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            self.assertEqual(ledger["backend"], "cpu")
            self.assertTrue(ledger["feasible"])
            self.assertEqual(ledger["best_penalty"], 0.0)
            self.assertGreaterEqual(len(ledger["ledger"]), 1)

    def test_ledger_command_summarizes_runtime_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.json"
            run = _run_cli(
                "run",
                str(TINY_SPEC),
                "--ledger-out",
                str(ledger_path),
                "--max-iters",
                "2",
            )
            self.assertEqual(run.returncode, 0, run.stderr)

            completed = _run_cli("ledger", str(ledger_path))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["backend"], "cpu")
        self.assertTrue(summary["feasible"])
        self.assertGreaterEqual(summary["rows"], 1)
        self.assertIn("active_violation_count", summary["last"])

    def test_run_auto_routes_qubo_family(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "qubo-report.json"
            artifact_dir = Path(tmpdir) / "artifacts"
            completed = _run_cli(
                "run",
                str(TINY_QUBO),
                "--family",
                "auto",
                "--ledger-out",
                str(report_path),
                "--artifact-dir",
                str(artifact_dir),
                "--run-id",
                "qubo_cli",
                "--max-iters",
                "2",
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "apc.qubo_cpu_reference_execution.v1")
            self.assertEqual(report["problem_family"], "qubo")
            self.assertEqual(report["backend"], "cpu")
            self.assertEqual(report["status"], "implemented")
            self.assertIn("evidence", report)
            self.assertIn("run_artifacts", report)
            self.assertTrue(report_path.exists())
            self.assertTrue((artifact_dir / "qubo_cli" / "metadata.json").exists())

    def test_run_auto_routes_maxsat_family(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "maxsat-report.json"
            completed = _run_cli(
                "run",
                str(TINY_MAXSAT),
                "--family",
                "auto",
                "--ledger-out",
                str(report_path),
                "--max-iters",
                "2",
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "apc.maxsat_runtime_route.v1")
            self.assertEqual(report["problem_family"], "maxsat")
            self.assertEqual(report["backend"], "cpu")
            self.assertEqual(report["status"], "implemented")
            self.assertIn("evidence", report)
            self.assertTrue(report_path.exists())

    def test_run_unsupported_family_fails_with_structured_status(self):
        completed = _run_cli(
            "run",
            str(TINY_SPEC),
            "--family",
            "unknown_family",
        )

        self.assertEqual(completed.returncode, 1)
        report = json.loads(completed.stdout)
        self.assertEqual(report["schema"], "apc.runtime_family_route.v1")
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["problem_family"], "unknown_family")
        self.assertIn("unsupported family", report["reason"])


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "apc.cli", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


if __name__ == "__main__":
    unittest.main()
