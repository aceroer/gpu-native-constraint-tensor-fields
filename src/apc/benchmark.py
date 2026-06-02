"""Benchmark harness for APC native workflows."""

from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .io_json import load_problem_json
from .layout import layout_summary, plan_layout
from .ledger import ledger_to_dicts
from .lowering import lower_problem_to_ctir
from .runtime_cpu import RuntimeConfig, run_repair


@dataclass(frozen=True)
class BenchmarkConfig:
    """Benchmark controls."""

    backend: str = "cpu"
    max_iters: int = 8
    batch_size: int = 4
    seed: int = 0
    penalty_weight: float = 10.0

    def __post_init__(self) -> None:
        if self.backend not in ("cpu", "cuda"):
            raise ValueError("benchmark backend must be cpu or cuda")
        if self.max_iters < 0:
            raise ValueError("max_iters must be nonnegative")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.penalty_weight <= 0.0:
            raise ValueError("penalty_weight must be positive")


def run_benchmark(spec_path: str | Path, config: BenchmarkConfig | None = None) -> dict[str, Any]:
    """Run a benchmark and return a JSON-ready report."""

    cfg = config or BenchmarkConfig()
    if cfg.backend == "cuda":
        return _unavailable_cuda_report(spec_path, cfg)

    start = time.perf_counter()
    problem_spec = load_problem_json(spec_path)
    ctir = lower_problem_to_ctir(problem_spec, batch_size=cfg.batch_size)
    layout_start = time.perf_counter()
    layout_plan = plan_layout(ctir)
    layout_elapsed = time.perf_counter() - layout_start

    runtime_config = RuntimeConfig(
        max_iters=cfg.max_iters,
        batch_size=cfg.batch_size,
        seed=cfg.seed,
        penalty_weight=cfg.penalty_weight,
    )
    kernel_start = time.perf_counter()
    result = run_repair(ctir, config=runtime_config)
    kernel_elapsed = time.perf_counter() - kernel_start
    end_to_end = time.perf_counter() - start

    ledger = ledger_to_dicts(result.ledger)
    return {
        "schema": "apc.benchmark.v1",
        "problem": {
            "path": str(spec_path),
            "family": "binary_milp",
        },
        "backend": {
            "name": "cpu",
            "available": True,
        },
        "config": {
            "max_iters": cfg.max_iters,
            "batch_size": cfg.batch_size,
            "seed": cfg.seed,
            "penalty_weight": cfg.penalty_weight,
        },
        "metrics": {
            "best_objective": result.best_objective,
            "best_penalty": result.best_penalty,
            "feasible_count": ledger[-1]["feasible_count"],
            "violation_decay": _violation_decay(ledger),
            "kernel_time_s": kernel_elapsed,
            "copy_time_s": 0.0,
            "layout_conversion_time_s": layout_elapsed,
            "end_to_end_time_s": end_to_end,
        },
        "layout": {
            "costs": layout_summary(layout_plan)["costs"],
        },
        "ledger": ledger,
        "notes": [
            "CPU benchmark reports operator runtime as kernel_time_s for schema compatibility.",
            "No GPU speedup is claimed without CUDA copy-time accounting.",
        ],
    }


def write_benchmark_report(report: dict[str, Any], path: str | Path) -> None:
    """Write a benchmark report as stable JSON."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _violation_decay(ledger: list[dict[str, float | int]]) -> list[int]:
    return [int(row["active_violation_count"]) for row in ledger]


def _unavailable_cuda_report(spec_path: str | Path, config: BenchmarkConfig) -> dict[str, Any]:
    return {
        "schema": "apc.benchmark.v1",
        "problem": {
            "path": str(spec_path),
            "family": "binary_milp",
        },
        "backend": {
            "name": "cuda",
            "available": False,
            "reason": "nvcc not found" if shutil.which("nvcc") is None else "CUDA benchmark runtime is not wired yet",
        },
        "config": {
            "max_iters": config.max_iters,
            "batch_size": config.batch_size,
            "seed": config.seed,
            "penalty_weight": config.penalty_weight,
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
            "CUDA benchmark is reported separately and unavailable on this machine.",
            "No GPU speedup is claimed without copy-time accounting.",
        ],
    }
