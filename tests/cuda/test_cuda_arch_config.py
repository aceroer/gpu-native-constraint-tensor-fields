import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from apc import BenchmarkConfig, run_cuda_benchmark_report

from .cuda_diff_utils import nvcc_arch_args


ROOT = Path(__file__).resolve().parents[2]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"


class CUDAArchConfigTests(unittest.TestCase):
    def test_diff_helper_reads_apc_cuda_arch(self):
        with patch.dict(os.environ, {"APC_CUDA_ARCH": "sm_89"}):
            self.assertEqual(nvcc_arch_args(), ["-arch=sm_89"])

    def test_diff_helper_omits_arch_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(nvcc_arch_args(), [])

    def test_cuda_benchmark_reads_apc_cuda_arch(self):
        with patch.dict(os.environ, {"APC_CUDA_ARCH": "sm_89"}):
            report = run_cuda_benchmark_report(
                TINY_SPEC,
                BenchmarkConfig(backend="cuda", max_iters=2),
                element_count=16,
            )

        self.assertEqual(report["config"]["cuda_arch"], "sm_89")

    def test_cli_uses_apc_cuda_arch_when_flag_is_absent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "cuda.json"
            env = dict(os.environ)
            env["APC_CUDA_ARCH"] = "sm_89"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_cuda_bench.py",
                    str(TINY_SPEC),
                    "--out",
                    str(output),
                    "--element-count",
                    "16",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
