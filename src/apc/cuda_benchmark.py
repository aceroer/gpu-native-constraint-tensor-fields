"""CUDA benchmark timing report helpers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from .benchmark import BenchmarkConfig


ROOT = Path(__file__).resolve().parents[2]
TIMING_PROBE = ROOT / "cuda" / "bench" / "timing_probe.cu"


def run_cuda_benchmark_report(
    spec_path: str | Path,
    config: BenchmarkConfig | None = None,
    *,
    element_count: int = 1024,
    cuda_arch: str | None = None,
) -> dict[str, Any]:
    """Run the CUDA timing probe when available and return benchmark JSON."""

    cfg = config or BenchmarkConfig(backend="cuda")
    resolved_cuda_arch = cuda_arch or _env_cuda_arch()
    if cfg.backend != "cuda":
        raise ValueError("CUDA benchmark report requires backend=cuda")
    nvcc = shutil.which("nvcc")
    if nvcc is None:
        return _unavailable_report(spec_path, cfg, "nvcc not found", cuda_arch=resolved_cuda_arch)

    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmpdir:
        binary = Path(tmpdir) / "apc_cuda_timing_probe"
        build_cmd = [nvcc, "-std=c++17", str(TIMING_PROBE), "-o", str(binary)]
        if resolved_cuda_arch:
            build_cmd.insert(1, f"-arch={resolved_cuda_arch}")
        build = subprocess.run(
            build_cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if build.returncode != 0:
            return _unavailable_report(
                spec_path,
                cfg,
                f"nvcc build failed: {build.stderr.strip()}",
                cuda_arch=resolved_cuda_arch,
            )
        run = subprocess.run(
            [str(binary), str(element_count)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    end_to_end = time.perf_counter() - start

    if run.returncode != 0:
        reason = _probe_reason(run.stderr)
        return _unavailable_report(spec_path, cfg, reason, cuda_arch=resolved_cuda_arch)

    probe = json.loads(run.stdout)
    copy_time = float(probe["copy_time_s"])
    kernel_time = float(probe["kernel_time_s"])
    return {
        "schema": "apc.benchmark.v1",
        "problem": {
            "path": str(spec_path),
            "family": "binary_milp",
        },
        "backend": {
            "name": "cuda",
            "available": True,
        },
        "config": {
            "max_iters": cfg.max_iters,
            "batch_size": cfg.batch_size,
            "seed": cfg.seed,
            "penalty_weight": cfg.penalty_weight,
            "cuda_arch": resolved_cuda_arch,
        },
        "metrics": {
            "best_objective": None,
            "best_penalty": None,
            "feasible_count": 0,
            "violation_decay": [],
            "kernel_time_s": kernel_time,
            "copy_time_s": copy_time,
            "layout_conversion_time_s": 0.0,
            "end_to_end_time_s": end_to_end,
        },
        "layout": {
            "costs": [],
        },
        "ledger": [],
        "notes": [
            "CUDA timing probe reports copy and kernel timing separately.",
            "No speedup ratio is emitted by CUDA-only benchmark reports.",
        ],
    }


def _unavailable_report(
    spec_path: str | Path,
    config: BenchmarkConfig,
    reason: str,
    *,
    cuda_arch: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": "apc.benchmark.v1",
        "problem": {
            "path": str(spec_path),
            "family": "binary_milp",
        },
        "backend": {
            "name": "cuda",
            "available": False,
            "reason": reason,
        },
        "config": {
            "max_iters": config.max_iters,
            "batch_size": config.batch_size,
            "seed": config.seed,
            "penalty_weight": config.penalty_weight,
            "cuda_arch": cuda_arch,
        },
        "metrics": {
            "best_objective": None,
            "best_penalty": None,
            "feasible_count": 0,
            "violation_decay": [],
            "kernel_time_s": 0.0,
            "copy_time_s": 0.0,
            "layout_conversion_time_s": 0.0,
            "end_to_end_time_s": 0.0,
        },
        "layout": {
            "costs": [],
        },
        "ledger": [],
        "notes": [
            "CUDA benchmark is unavailable and no speedup is claimed.",
            "CUDA reports must include copy-time accounting before comparisons.",
        ],
    }


def _env_cuda_arch() -> str | None:
    value = os.environ.get("APC_CUDA_ARCH", "").strip()
    return value or None


def _probe_reason(stderr: str) -> str:
    text = stderr.strip()
    if not text:
        return "CUDA timing probe failed"
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text
    reason = payload.get("reason")
    return str(reason) if reason else text
