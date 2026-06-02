"""CLI entrypoint for the vector-native repair demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vector_state_repair.demo import run_vector_state_repair_demo, write_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the vector-native repair demo.")
    parser.add_argument(
        "spec",
        nargs="?",
        default="examples/specs/binary_milp_tiny.json",
        help="Path to a native binary MILP JSON spec.",
    )
    parser.add_argument("--out", help="Optional output JSON path.")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--penalty-weight", type=float, default=10.0)
    parser.add_argument("--diversity-weight", type=float, default=0.0)
    args = parser.parse_args()

    report = run_vector_state_repair_demo(
        args.spec,
        batch_size=args.batch_size,
        top_k=args.top_k,
        penalty_weight=args.penalty_weight,
        diversity_weight=args.diversity_weight,
    )
    if args.out:
        write_report(report, Path(args.out))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
