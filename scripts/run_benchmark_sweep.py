#!/usr/bin/env python3
"""Run benchmark sweep configs and write factual JSON summaries."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from apc.benchmark import BenchmarkConfig, run_benchmark, write_benchmark_report
from apc.benchmark_sweep import BenchmarkSweepCase, load_benchmark_sweep_config
from apc.readings.maxsat import run_maxsat_runtime_route_from_json
from apc.runtime_qubo_cpu import QUBORuntimeConfig, describe_qubo_cpu_reference_execution_from_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run_benchmark_sweep.py")
    parser.add_argument("config", help="benchmark sweep config JSON path")
    parser.add_argument("--out", help="optional sweep summary JSON output path")
    args = parser.parse_args(argv)

    try:
        summary = run_benchmark_sweep(args.config)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.out:
        output = _resolve_path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "ok" else 1


def run_benchmark_sweep(config_path: str | Path) -> dict[str, Any]:
    """Run all cases in a sweep config and return a JSON-ready summary."""

    config = load_benchmark_sweep_config(config_path)
    cases = [_run_case(case) for case in config.cases]
    failed_cases = [case for case in cases if case["status"] == "failed"]
    return {
        "schema": "apc.benchmark_sweep.v1",
        "status": "failed" if failed_cases else "ok",
        "config_schema": "apc.benchmark_sweep_config.v1",
        "config_path": str(config_path),
        "name": config.name,
        "case_count": len(cases),
        "cases": cases,
        "timing_fields": list(config.timing_fields),
        "notes": list(config.notes),
    }


def _run_case(case: BenchmarkSweepCase) -> dict[str, Any]:
    spec_path = _resolve_path(case.spec)
    out_path = _resolve_path(case.out)
    problem_family = _problem_family(spec_path)
    operator = _operator_name(problem_family, case.backend)
    try:
        report = _run_family_benchmark(case, spec_path, problem_family, operator)
        write_benchmark_report(report, out_path)
    except Exception as exc:
        return {
            "name": case.name,
            "status": "failed",
            "backend": case.backend,
            "problem_family": problem_family,
            "operator": operator,
            "spec": case.spec,
            "out": case.out,
            "error": str(exc),
        }

    backend = report.get("backend", {})
    metrics = report.get("metrics", {})
    available = bool(backend.get("available"))
    status = "ok" if available else "unavailable"
    return {
        "name": case.name,
        "status": status,
        "backend": case.backend,
        "problem_family": problem_family,
        "operator": operator,
        "backend_available": available,
        "backend_reason": backend.get("reason"),
        "spec": case.spec,
        "out": case.out,
        "report_schema": report.get("schema"),
        "timing": {
            "kernel_time_s": metrics.get("kernel_time_s"),
            "copy_time_s": metrics.get("copy_time_s"),
            "layout_conversion_time_s": metrics.get("layout_conversion_time_s"),
            "end_to_end_time_s": metrics.get("end_to_end_time_s"),
        },
    }


def _run_family_benchmark(
    case: BenchmarkSweepCase,
    spec_path: Path,
    problem_family: str,
    operator: str,
) -> dict[str, Any]:
    if problem_family == "binary_milp":
        report = run_benchmark(
            spec_path,
            BenchmarkConfig(
                backend=case.backend,
                max_iters=case.max_iters,
                batch_size=case.batch_size,
                seed=case.seed,
                penalty_weight=case.penalty_weight,
            ),
        )
        problem = report.setdefault("problem", {})
        if isinstance(problem, dict):
            problem["operator"] = operator
        return report
    if case.backend == "cuda":
        return _unavailable_family_report(case, spec_path, problem_family, operator)
    if problem_family == "qubo":
        return _qubo_cpu_benchmark(case, spec_path, operator)
    if problem_family == "maxsat":
        return _maxsat_cpu_benchmark(case, spec_path, operator)
    raise ValueError(f"unsupported benchmark problem family: {problem_family}")


def _qubo_cpu_benchmark(case: BenchmarkSweepCase, spec_path: Path, operator: str) -> dict[str, Any]:
    start = time.perf_counter()
    report = describe_qubo_cpu_reference_execution_from_json(
        spec_path,
        config=QUBORuntimeConfig(
            max_iters=case.max_iters,
            batch_size=case.batch_size,
            seed=case.seed,
        ),
    )
    elapsed = time.perf_counter() - start
    best = report.get("best", {})
    return _family_report(
        case=case,
        spec_path=spec_path,
        problem_family="qubo",
        operator=operator,
        available=report.get("status") == "implemented",
        metrics={
            "best_objective": best.get("objective"),
            "best_penalty": best.get("penalty"),
            "best_energy": best.get("energy"),
            "move_count": report.get("move_count"),
            "kernel_time_s": elapsed,
            "copy_time_s": 0.0,
            "layout_conversion_time_s": 0.0,
            "end_to_end_time_s": elapsed,
        },
        ledger=report.get("ledger", []),
        notes=[
            "QUBO CPU benchmark uses the deterministic reference route.",
            "No acceleration comparison is inferred from this report.",
        ],
    )


def _maxsat_cpu_benchmark(case: BenchmarkSweepCase, spec_path: Path, operator: str) -> dict[str, Any]:
    start = time.perf_counter()
    report = run_maxsat_runtime_route_from_json(
        spec_path,
        batch_size=case.batch_size,
        max_iters=case.max_iters,
        seed=case.seed,
    )
    elapsed = time.perf_counter() - start
    result = report.get("result", {})
    return _family_report(
        case=case,
        spec_path=spec_path,
        problem_family="maxsat",
        operator=operator,
        available=report.get("status") == "implemented",
        metrics={
            "best_objective": result.get("evaluation", {}).get("objective"),
            "best_penalty": result.get("best_penalty"),
            "unsatisfied_count": sum(1 for value in result.get("unsatisfied", []) if value),
            "kernel_time_s": elapsed,
            "copy_time_s": 0.0,
            "layout_conversion_time_s": 0.0,
            "end_to_end_time_s": elapsed,
        },
        ledger=report.get("ledger", []),
        notes=[
            "MaxSAT CPU benchmark uses the deterministic reference route.",
            "No acceleration comparison is inferred from this report.",
        ],
    )


def _family_report(
    *,
    case: BenchmarkSweepCase,
    spec_path: Path,
    problem_family: str,
    operator: str,
    available: bool,
    metrics: dict[str, Any],
    ledger: Any,
    notes: list[str],
    backend_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": "apc.benchmark.v1",
        "problem": {
            "path": str(spec_path),
            "family": problem_family,
            "operator": operator,
        },
        "backend": {
            "name": case.backend,
            "available": available,
            "reason": backend_reason,
        },
        "config": {
            "max_iters": case.max_iters,
            "batch_size": case.batch_size,
            "seed": case.seed,
            "penalty_weight": case.penalty_weight,
        },
        "metrics": metrics,
        "layout": {
            "costs": [],
        },
        "ledger": ledger,
        "notes": notes,
    }


def _unavailable_family_report(
    case: BenchmarkSweepCase,
    spec_path: Path,
    problem_family: str,
    operator: str,
) -> dict[str, Any]:
    return _family_report(
        case=case,
        spec_path=spec_path,
        problem_family=problem_family,
        operator=operator,
        available=False,
        metrics={
            "best_objective": None,
            "best_penalty": None,
            "kernel_time_s": 0.0,
            "copy_time_s": 0.0,
            "layout_conversion_time_s": 0.0,
            "end_to_end_time_s": 0.0,
        },
        ledger=[],
        notes=[
            f"CUDA benchmark for {problem_family} is unavailable in this sweep runner.",
            "No acceleration comparison is inferred from this report.",
        ],
        backend_reason=f"CUDA benchmark for {problem_family} is unavailable in this sweep runner",
    )


def _problem_family(spec_path: Path) -> str:
    payload = json.loads(spec_path.read_text(encoding="utf-8"))
    problem_type = payload.get("problem_type")
    if problem_type == "binary_milp":
        return "binary_milp"
    if problem_type == "qubo":
        return "qubo"
    if problem_type == "weighted_maxsat":
        return "maxsat"
    constraints = payload.get("constraints")
    if isinstance(constraints, dict) and "linear_csr" in constraints:
        return "binary_milp"
    raise ValueError(f"unsupported benchmark problem_type: {problem_type}")


def _operator_name(problem_family: str, backend: str) -> str:
    if problem_family == "binary_milp":
        return "repair_runtime"
    if problem_family == "qubo":
        return "qubo_cpu_reference" if backend == "cpu" else "qubo_cuda_parity"
    if problem_family == "maxsat":
        return "maxsat_cpu_reference" if backend == "cpu" else "maxsat_cuda_parity"
    return "unknown"


def _resolve_path(path: str | Path) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    return ROOT / value


if __name__ == "__main__":
    raise SystemExit(main())
