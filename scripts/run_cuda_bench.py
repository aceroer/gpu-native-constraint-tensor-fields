#!/usr/bin/env python3
"""Run CUDA timing benchmark reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from apc.benchmark import BenchmarkConfig, write_benchmark_report
from apc.cuda_benchmark import run_cuda_benchmark_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run_cuda_bench.py")
    parser.add_argument("spec")
    parser.add_argument("--out", default="benchmarks/latest_cuda.json")
    parser.add_argument("--max-iters", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--penalty-weight", type=float, default=10.0)
    parser.add_argument("--element-count", type=int, default=1024)
    args = parser.parse_args(argv)

    config = BenchmarkConfig(
        backend="cuda",
        max_iters=args.max_iters,
        batch_size=args.batch_size,
        seed=args.seed,
        penalty_weight=args.penalty_weight,
    )
    report = run_cuda_benchmark_report(args.spec, config, element_count=args.element_count)
    write_benchmark_report(report, args.out)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
