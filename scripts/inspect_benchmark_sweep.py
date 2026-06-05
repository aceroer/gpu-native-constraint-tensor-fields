#!/usr/bin/env python3
"""Summarize benchmark sweep reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SWEEP_SCHEMA = "apc.benchmark_sweep.v1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="inspect_benchmark_sweep.py")
    parser.add_argument("path", help="benchmark sweep summary JSON path")
    parser.add_argument("--out", help="optional compact summary JSON output path")
    args = parser.parse_args(argv)

    summary = inspect_benchmark_sweep(Path(args.path))
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] != "failed" else 1


def inspect_benchmark_sweep(path: Path) -> dict[str, Any]:
    """Return a compact factual summary for an apc.benchmark_sweep.v1 file."""

    sweep = _load_json(path)
    if sweep is None:
        return _failed_summary(path=path, reason="missing_or_invalid_json")
    if sweep.get("schema") != SWEEP_SCHEMA:
        return _failed_summary(
            path=path,
            reason="unsupported_schema",
            observed_schema=_string_or_none(sweep.get("schema")),
        )

    cases = _case_summaries(sweep.get("cases"))
    return {
        "schema": "apc.benchmark_sweep_summary.v1",
        "source_schema": SWEEP_SCHEMA,
        "source_path": str(path),
        "status": _string_or_value(sweep.get("status"), default="unknown"),
        "name": _string_or_value(sweep.get("name"), default="unknown"),
        "config_path": _string_or_value(sweep.get("config_path"), default="unknown"),
        "case_count": len(cases),
        "case_statuses": cases,
        "timing_fields": _string_list(sweep.get("timing_fields")),
        "unavailable_cases": [case["name"] for case in cases if case["status"] == "unavailable"],
        "failed_cases": [case["name"] for case in cases if case["status"] == "failed"],
        "notes": [
            "Summary is factual benchmark sweep inspection only.",
            "No performance claim is inferred from this summary.",
        ],
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _failed_summary(
    *,
    path: Path,
    reason: str,
    observed_schema: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": "apc.benchmark_sweep_summary.v1",
        "source_schema": observed_schema,
        "source_path": str(path),
        "status": "failed",
        "reason": reason,
        "name": "unknown",
        "config_path": "unknown",
        "case_count": 0,
        "case_statuses": [],
        "timing_fields": [],
        "unavailable_cases": [],
        "failed_cases": [],
        "notes": [
            "Summary is factual benchmark sweep inspection only.",
            "No performance claim is inferred from this summary.",
        ],
    }


def _case_summaries(cases: Any) -> list[dict[str, Any]]:
    if not isinstance(cases, list):
        return []
    summaries: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict):
            continue
        summaries.append(
            {
                "name": _string_or_value(case.get("name"), default="unknown"),
                "status": _string_or_value(case.get("status"), default="unknown"),
                "backend": _string_or_value(case.get("backend"), default="unknown"),
                "problem_family": _string_or_value(case.get("problem_family"), default="unknown"),
                "backend_available": bool(case.get("backend_available")),
                "backend_reason": _string_or_none(case.get("backend_reason")),
                "spec": _string_or_value(case.get("spec"), default="unknown"),
                "out": _string_or_value(case.get("out"), default="unknown"),
                "report_schema": _string_or_none(case.get("report_schema")),
                "timing": _timing_summary(case.get("timing")),
            }
        )
    return summaries


def _timing_summary(timing: Any) -> dict[str, float | int | None]:
    if not isinstance(timing, dict):
        return {}
    return {
        "kernel_time_s": _number_or_none(timing.get("kernel_time_s")),
        "copy_time_s": _number_or_none(timing.get("copy_time_s")),
        "layout_conversion_time_s": _number_or_none(timing.get("layout_conversion_time_s")),
        "end_to_end_time_s": _number_or_none(timing.get("end_to_end_time_s")),
    }


def _number_or_none(value: Any) -> float | int | None:
    return value if isinstance(value, (float, int)) and not isinstance(value, bool) else None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _string_or_value(value: Any, *, default: str) -> str:
    return value if isinstance(value, str) else default


if __name__ == "__main__":
    raise SystemExit(main())
