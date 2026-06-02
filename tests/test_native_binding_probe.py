import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from apc.io_json import load_problem_json
from apc.lowering import lower_problem_to_ctir
from apc.runtime_cpu import RuntimeConfig, run_repair
from scripts import probe_native_host


ROOT = Path(__file__).resolve().parents[1]


class NativeBindingProbeTests(unittest.TestCase):
    def test_probe_reports_unavailable_without_cmake(self):
        with mock.patch.object(probe_native_host.shutil, "which", return_value=None):
            report = probe_native_host.probe_native_host(build_dir=Path("/tmp/unused-native-probe"))

        self.assertEqual(report["schema"], "apc.native_host_probe.v1")
        self.assertEqual(report["status"], "unavailable")
        self.assertEqual(report["reason"], "cmake_not_found")
        self.assertEqual(report["steps"], [])
        self.assertIn("native_dir", report["paths"])

    def test_probe_reports_failed_configure(self):
        def fake_run(*args, **kwargs):
            return subprocess.CompletedProcess(args=args[0], returncode=2, stdout="", stderr="bad")

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(probe_native_host.shutil, "which", return_value="/usr/bin/cmake"):
                with mock.patch.object(probe_native_host.subprocess, "run", side_effect=fake_run):
                    report = probe_native_host.probe_native_host(build_dir=Path(tmpdir))

        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["reason"], "native_probe_step_failed")
        self.assertEqual(report["steps"][0]["name"], "configure")
        self.assertEqual(report["steps"][0]["returncode"], 2)
        self.assertTrue(report["steps"][1]["skipped"])

    def test_probe_command_writes_json_report(self):
        if shutil.which("cmake") is None:
            self.skipTest("cmake is not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            out = tmp / "probe.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/probe_native_host.py",
                    "--build-dir",
                    str(tmp / "build"),
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
        self.assertEqual(stdout_report["schema"], "apc.native_host_probe.v1")
        self.assertEqual(file_report["status"], "ok")
        self.assertEqual([step["name"] for step in file_report["steps"]], ["configure", "build"])

    def test_probe_configure_only(self):
        if shutil.which("cmake") is None:
            self.skipTest("cmake is not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            report = probe_native_host.probe_native_host(build_dir=Path(tmpdir), build=False)

        self.assertEqual(report["status"], "ok")
        self.assertEqual([step["name"] for step in report["steps"]], ["configure"])

    def test_probe_stays_factual_only(self):
        with mock.patch.object(probe_native_host.shutil, "which", return_value=None):
            report = probe_native_host.probe_native_host(build_dir=Path("/tmp/unused-native-probe"))

        text = json.dumps(report).lower()
        self.assertIn("optional evidence", text)
        self.assertNotIn("speedup", text)
        self.assertNotIn("compatible with", text)

    def test_probe_does_not_change_python_runtime_behavior(self):
        spec = load_problem_json(ROOT / "examples" / "specs" / "binary_milp_tiny.json")
        problem = lower_problem_to_ctir(spec, batch_size=4)
        config = RuntimeConfig(max_iters=2, batch_size=4, seed=0)

        before = run_repair(problem, config=config)
        with tempfile.TemporaryDirectory() as tmpdir:
            _ = probe_native_host.probe_native_host(build_dir=Path(tmpdir), build=False)
        after = run_repair(problem, config=config)

        self.assertEqual(before.best_state, after.best_state)
        self.assertEqual(before.best_objective, after.best_objective)
        self.assertEqual(before.best_penalty, after.best_penalty)
        self.assertEqual(before.ledger, after.ledger)


if __name__ == "__main__":
    unittest.main()
