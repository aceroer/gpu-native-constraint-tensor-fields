import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from apc.io_json import load_problem_json
from apc.lowering import lower_problem_to_ctir
from apc.runtime_cpu import RuntimeConfig, run_repair


ROOT = Path(__file__).resolve().parents[1]
NATIVE_DIR = ROOT / "native"
HEADER = NATIVE_DIR / "include" / "apc_runtime.hpp"
SHIM = NATIVE_DIR / "src" / "cpu_operator_shim.cpp"


class NativeCPUOperatorShimTests(unittest.TestCase):
    def test_shim_files_exist(self):
        self.assertTrue(HEADER.exists(), HEADER)
        self.assertTrue(SHIM.exists(), SHIM)
        self.assertTrue((NATIVE_DIR / "CMakeLists.txt").exists())

    def test_header_declares_probe_functions(self):
        text = HEADER.read_text(encoding="utf-8")

        self.assertIn("OperatorCallRecord make_probe_operator_call_record()", text)
        self.assertIn("RuntimeStatus native_probe_status()", text)

    def test_shim_returns_public_operator_call_record(self):
        text = SHIM.read_text(encoding="utf-8")

        self.assertIn("make_probe_operator_call_record", text)
        self.assertIn("native_cpu_probe", text)
        self.assertIn("RuntimeStatus::implemented", text)
        self.assertIn("empty_runtime_timing()", text)
        self.assertIn("state.candidate_major", text)
        self.assertIn("operator_call.probe", text)
        self.assertNotIn("speedup", text.lower())
        self.assertNotIn("compatible", text.lower())

    def test_native_build_can_be_disabled(self):
        if shutil.which("cmake") is None:
            self.skipTest("cmake is not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            completed = subprocess.run(
                [
                    "cmake",
                    "-S",
                    str(NATIVE_DIR),
                    "-B",
                    tmpdir,
                    "-DAPC_ENABLE_NATIVE_HOST=OFF",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("APC native host runtime disabled", completed.stdout + completed.stderr)

    def test_native_shim_builds_when_cmake_exists(self):
        if shutil.which("cmake") is None:
            self.skipTest("cmake is not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            configure = subprocess.run(
                [
                    "cmake",
                    "-S",
                    str(NATIVE_DIR),
                    "-B",
                    tmpdir,
                    "-DAPC_ENABLE_NATIVE_HOST=ON",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(configure.returncode, 0, configure.stderr)

            build = subprocess.run(
                ["cmake", "--build", tmpdir],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(build.returncode, 0, build.stderr)

    def test_shim_does_not_change_python_runtime_behavior(self):
        spec = load_problem_json(ROOT / "examples" / "specs" / "binary_milp_tiny.json")
        problem = lower_problem_to_ctir(spec, batch_size=4)
        config = RuntimeConfig(max_iters=2, batch_size=4, seed=0)

        before = run_repair(problem, config=config)
        _ = SHIM.read_text(encoding="utf-8")
        after = run_repair(problem, config=config)

        self.assertEqual(before.best_state, after.best_state)
        self.assertEqual(before.best_objective, after.best_objective)
        self.assertEqual(before.best_penalty, after.best_penalty)
        self.assertEqual(before.ledger, after.ledger)


if __name__ == "__main__":
    unittest.main()
