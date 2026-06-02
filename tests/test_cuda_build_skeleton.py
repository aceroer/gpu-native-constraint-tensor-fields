import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CUDA_DIR = ROOT / "cuda"
HEADER = CUDA_DIR / "include" / "apc_runtime.h"


class CUDABuildSkeletonTests(unittest.TestCase):
    def test_phase5_files_exist(self):
        expected = [
            CUDA_DIR / "CMakeLists.txt",
            HEADER,
            CUDA_DIR / "src" / "linear_csr_eval.cu",
            CUDA_DIR / "src" / "violation_reduce.cu",
            CUDA_DIR / "src" / "projection.cu",
            CUDA_DIR / "src" / "clause_eval.cu",
        ]

        for path in expected:
            self.assertTrue(path.exists(), path)

    def test_header_abi_is_operator_based_with_status_codes(self):
        text = HEADER.read_text(encoding="utf-8")

        self.assertIn("typedef enum", text)
        self.assertIn("APC_OK = 0", text)
        self.assertIn("APC_ERR_INVALID_ARGUMENT", text)
        self.assertIn("APC_ERR_CUDA", text)
        for name in (
            "apc_eval_linear_csr",
            "apc_rectify_linear_violation",
            "apc_reduce_weighted_penalty",
            "apc_project_binary",
            "apc_eval_clause_csr",
        ):
            self.assertIn(name, text)

    def test_launch_wrappers_return_status_codes(self):
        for path in (
            CUDA_DIR / "src" / "linear_csr_eval.cu",
            CUDA_DIR / "src" / "violation_reduce.cu",
            CUDA_DIR / "src" / "projection.cu",
            CUDA_DIR / "src" / "clause_eval.cu",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIn("extern \"C\" APC_Status", text)
            self.assertIn("APC_ERR_INVALID_ARGUMENT", text)
            self.assertIn("cudaGetLastError()", text)

    def test_cmake_configure_succeeds_when_cuda_disabled(self):
        if shutil.which("cmake") is None:
            self.skipTest("cmake is not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            completed = subprocess.run(
                [
                    "cmake",
                    "-S",
                    str(CUDA_DIR),
                    "-B",
                    tmpdir,
                    "-DAPC_ENABLE_CUDA=OFF",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("APC CUDA runtime disabled", completed.stdout + completed.stderr)

    def test_cmake_build_succeeds_when_nvcc_is_available(self):
        if shutil.which("cmake") is None:
            self.skipTest("cmake is not installed")
        if shutil.which("nvcc") is None:
            self.skipTest("nvcc is not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            configure = subprocess.run(
                [
                    "cmake",
                    "-S",
                    str(CUDA_DIR),
                    "-B",
                    tmpdir,
                    "-DAPC_ENABLE_CUDA=ON",
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


if __name__ == "__main__":
    unittest.main()
