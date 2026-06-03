"""Helpers for CUDA differential tests."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CUDA_DIR = ROOT / "cuda"


def require_nvcc(testcase) -> str:
    nvcc = shutil.which("nvcc")
    if nvcc is None:
        testcase.skipTest("nvcc is not installed")
    return nvcc


def nvcc_arch_args() -> list[str]:
    """Return optional nvcc architecture args from APC_CUDA_ARCH."""

    arch = os.environ.get("APC_CUDA_ARCH", "").strip()
    return [f"-arch={arch}"] if arch else []


def compile_and_run_harness(
    testcase,
    source: str,
    sources: tuple[str, ...],
) -> str:
    nvcc = require_nvcc(testcase)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        harness = tmp / "harness.cu"
        binary = tmp / "harness"
        harness.write_text(source, encoding="utf-8")
        command = [
            nvcc,
            *nvcc_arch_args(),
            "-std=c++17",
            "-I",
            str(CUDA_DIR / "include"),
            str(harness),
            *[str(CUDA_DIR / path) for path in sources],
            "-o",
            str(binary),
        ]
        build = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        testcase.assertEqual(build.returncode, 0, build.stderr)

        run = subprocess.run(
            [str(binary)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        testcase.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout


def base_harness_prelude() -> str:
    return r'''
#include "apc_runtime.h"

#include <cuda_runtime.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <vector>

void require_ok(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "%s\n", message);
    std::exit(1);
  }
}

void require_status(APC_Status status, const char* message) {
  if (status != APC_OK) {
    std::fprintf(stderr, "%s: status=%d\n", message, static_cast<int>(status));
    std::exit(1);
  }
}

void require_cuda(cudaError_t err, const char* message) {
  if (err != cudaSuccess) {
    std::fprintf(stderr, "%s: %s\n", message, cudaGetErrorString(err));
    std::exit(1);
  }
}

template <typename T>
T* device_copy(const std::vector<T>& host) {
  T* device = nullptr;
  require_cuda(cudaMalloc(&device, sizeof(T) * host.size()), "cudaMalloc");
  require_cuda(
      cudaMemcpy(device, host.data(), sizeof(T) * host.size(), cudaMemcpyHostToDevice),
      "copy to device");
  return device;
}

template <typename T>
std::vector<T> host_copy(T* device, int count) {
  std::vector<T> host(count);
  require_cuda(
      cudaMemcpy(host.data(), device, sizeof(T) * count, cudaMemcpyDeviceToHost),
      "copy to host");
  return host;
}

void expect_close(double actual, double expected, double tol, const char* label) {
  if (std::fabs(actual - expected) > tol) {
    std::fprintf(stderr, "%s actual=%0.17g expected=%0.17g\n", label, actual, expected);
    std::exit(1);
  }
}
'''
