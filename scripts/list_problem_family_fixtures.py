#!/usr/bin/env python3
"""List public problem-family fixtures and compact checked reports."""

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

from apc.benchmark import BenchmarkConfig, run_benchmark
from apc.readings.maxsat import run_maxsat_runtime_route_from_json
from apc.readings.qubo import describe_qubo_lowering_from_json


FIXTURES = (
    {
        "name": "binary_milp_tiny",
        "family": "binary_milp",
        "spec": "examples/specs/binary_milp_tiny.json",
        "spec_schema": "apc.native_binary_milp_spec.v1",
        "route_status": "implemented",
        "execution_status": "implemented",
        "command": "PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-binary-milp-bench.json",
    },
    {
        "name": "maxsat_tiny",
        "family": "maxsat",
        "spec": "examples/specs/maxsat_tiny.json",
        "spec_schema": "apc.weighted_maxsat_spec.v1",
        "route_status": "implemented",
        "execution_status": "implemented",
        "command": "PYTHONPATH=src python3 -c \"from apc import run_maxsat_runtime_route_from_json; print(run_maxsat_runtime_route_from_json('examples/specs/maxsat_tiny.json'))\"",
    },
    {
        "name": "qubo_tiny",
        "family": "qubo",
        "spec": "examples/specs/qubo_tiny.json",
        "spec_schema": "apc.qubo_spec.v1",
        "route_status": "implemented",
        "execution_status": "planned",
        "command": "PYTHONPATH=src python3 -c \"from apc import describe_qubo_lowering_from_json; print(describe_qubo_lowering_from_json('examples/specs/qubo_tiny.json'))\"",
    },
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="list_problem_family_fixtures.py")
    parser.add_argument("--out", default=None, help="optional output JSON path")
    args = parser.parse_args(argv)

    report = list_problem_family_fixtures()
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "ok" else 1


def list_problem_family_fixtures() -> dict[str, Any]:
    """Return a JSON-ready index of public problem-family fixtures."""

    fixtures = [_fixture_to_dict(item) for item in FIXTURES]
    status = "ok" if all(item["exists"] and item["checked_report"]["status"] != "failed" for item in fixtures) else "failed"
    return {
        "schema": "apc.problem_family_fixture_index.v1",
        "status": status,
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
        "notes": [
            "Problem-family fixtures are public repository inspection evidence.",
            "Fixture records do not claim external solver compatibility.",
            "Planned execution routes remain marked as planned.",
            "No accelerator comparison claim is made by this index.",
        ],
    }


def _fixture_to_dict(item: dict[str, str]) -> dict[str, Any]:
    spec_path = ROOT / item["spec"]
    return {
        "name": item["name"],
        "family": item["family"],
        "spec": item["spec"],
        "spec_schema": item["spec_schema"],
        "exists": spec_path.exists(),
        "route_status": item["route_status"],
        "execution_status": item["execution_status"],
        "command": item["command"],
        "checked_report": _checked_report(item),
    }


def _checked_report(item: dict[str, str]) -> dict[str, Any]:
    spec_path = ROOT / item["spec"]
    if item["family"] == "binary_milp":
        report = run_benchmark(
            spec_path,
            BenchmarkConfig(backend="cpu", max_iters=2, batch_size=4, seed=0),
        )
        return {
            "schema": report["schema"],
            "status": "implemented",
            "backend": report["backend"]["name"],
            "available": report["backend"]["available"],
            "problem_family": report["problem"]["family"],
        }
    if item["family"] == "maxsat":
        report = run_maxsat_runtime_route_from_json(spec_path, batch_size=4, max_iters=4, seed=3)
        return {
            "schema": report["schema"],
            "status": report["status"],
            "backend": report["backend"],
            "problem_family": report["problem_family"],
        }
    if item["family"] == "qubo":
        report = describe_qubo_lowering_from_json(spec_path, batch_size=4)
        return {
            "schema": report["schema"],
            "status": report["status"],
            "execution_status": report["execution_status"],
            "problem_family": report["problem_family"],
        }
    return {
        "schema": None,
        "status": "failed",
        "reason": "unknown problem family",
    }


if __name__ == "__main__":
    raise SystemExit(main())
