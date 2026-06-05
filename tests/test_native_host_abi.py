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


class NativeHostABITests(unittest.TestCase):
    def test_native_host_files_exist(self):
        self.assertTrue(HEADER.exists(), HEADER)
        self.assertTrue((NATIVE_DIR / "CMakeLists.txt").exists())

    def test_header_names_public_status_codes_and_schemas(self):
        text = HEADER.read_text(encoding="utf-8")

        for status in ("implemented", "planned", "skipped", "failed", "unavailable"):
            self.assertIn(status, text)
        self.assertIn("apc.runtime_execution_contract.v1", text)
        self.assertIn("apc.operator_call_ledger.v1", text)
        self.assertIn("apc.runtime_status_codes.v1", text)
        self.assertIn("apc.native_host_bridge.v1", text)

    def test_header_names_operator_call_record_fields(self):
        text = HEADER.read_text(encoding="utf-8")

        self.assertIn("struct OperatorCallRecord", text)
        self.assertIn("step_name", text)
        self.assertIn("backend", text)
        self.assertIn("RuntimeStatus status", text)
        self.assertIn("RuntimeTiming timing", text)
        self.assertIn("operator_name", text)
        for timing in (
            "kernel_time_s",
            "copy_time_s",
            "layout_conversion_time_s",
            "end_to_end_time_s",
        ):
            self.assertIn(timing, text)

    def test_header_names_native_bridge_request_and_result_fields(self):
        text = HEADER.read_text(encoding="utf-8")

        self.assertIn("struct NativeOperatorRequest", text)
        self.assertIn("struct NativeOperatorResult", text)
        self.assertIn("struct NativeHostBridgeRecord", text)
        self.assertIn("operator_name", text)
        self.assertIn("problem_family", text)
        self.assertIn("RuntimeStatus status", text)
        self.assertIn("RuntimeTiming timing", text)
        self.assertIn("NativeOperatorRequest request", text)
        self.assertIn("NativeOperatorResult result", text)

    def test_native_cmake_can_be_disabled(self):
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

    def test_native_cmake_configures_when_cmake_exists(self):
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
                    "-DAPC_ENABLE_NATIVE_HOST=ON",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("APC native host runtime configured", completed.stdout + completed.stderr)

    def test_header_does_not_change_python_runtime_behavior(self):
        spec = load_problem_json(ROOT / "examples" / "specs" / "binary_milp_tiny.json")
        problem = lower_problem_to_ctir(spec, batch_size=4)
        config = RuntimeConfig(max_iters=2, batch_size=4, seed=0)

        before = run_repair(problem, config=config)
        _ = HEADER.read_text(encoding="utf-8")
        after = run_repair(problem, config=config)

        self.assertEqual(before.best_state, after.best_state)
        self.assertEqual(before.best_objective, after.best_objective)
        self.assertEqual(before.best_penalty, after.best_penalty)
        self.assertEqual(before.ledger, after.ledger)


if __name__ == "__main__":
    unittest.main()
