#!/usr/bin/env python3
"""Run benchmark sweep configs and write factual JSON summaries."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from apc.benchmark import BenchmarkConfig, run_benchmark, write_benchmark_report
from apc.benchmark_sweep import BenchmarkSweepCase, load_benchmark_sweep_config


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
    try:
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
        write_benchmark_report(report, out_path)
    except Exception as exc:
        return {
            "name": case.name,
            "status": "failed",
            "backend": case.backend,
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


def _resolve_path(path: str | Path) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    return ROOT / value


if __name__ == "__main__":
    raise SystemExit(main())
