#!/usr/bin/env python3
"""Run vector-native demo benchmark reports."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DEMO = ROOT / "examples" / "vector_state_repair"
for path in (SRC, DEMO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from vector_state_repair.demo import run_vector_state_repair_demo, write_report


def run_vector_demo_benchmark(
    spec_path: str | Path,
    *,
    batch_size: int = 4,
    top_k: int = 2,
    penalty_weight: float = 10.0,
    diversity_weight: float = 0.0,
) -> dict[str, Any]:
    """Run the vector-native demo and attach benchmark timing."""

    start = time.perf_counter()
    report = run_vector_state_repair_demo(
        spec_path,
        batch_size=batch_size,
        top_k=top_k,
        penalty_weight=penalty_weight,
        diversity_weight=diversity_weight,
    )
    elapsed = time.perf_counter() - start
    payload = report["payload"]
    payload["benchmark"] = {
        "schema": "apc.vector_demo_benchmark.v1",
        "runtime_path": [
            "CTIR",
            "StatePool",
            "BranchTensor",
            "ReductionGate",
            "InterfaceProjection",
        ],
        "timing": {
            "kernel_time_s": elapsed,
            "copy_time_s": 0.0,
            "layout_conversion_time_s": 0.0,
            "end_to_end_time_s": elapsed,
        },
        "notes": [
            "Vector-native demo benchmark reports CPU runtime path timing.",
            "No speedup claim is emitted without copy-time accounting.",
        ],
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run_vector_demo_bench.py")
    parser.add_argument("spec")
    parser.add_argument("--out", default="benchmarks/vector_native_report.latest.json")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--penalty-weight", type=float, default=10.0)
    parser.add_argument("--diversity-weight", type=float, default=0.0)
    args = parser.parse_args(argv)

    report = run_vector_demo_benchmark(
        args.spec,
        batch_size=args.batch_size,
        top_k=args.top_k,
        penalty_weight=args.penalty_weight,
        diversity_weight=args.diversity_weight,
    )
    write_report(report, args.out)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
