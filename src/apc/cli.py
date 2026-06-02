"""Command line interface for the native APC workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .inspect_ctir import inspect_ctir
from .io_json import load_problem_json
from .ledger import ledger_to_dicts
from .lowering import lower_problem_to_ctir
from .runtime_cpu import RuntimeConfig, run_repair_from_json


def main(argv: list[str] | None = None) -> int:
    """Run the APC command line interface."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        args.func(args)
    except Exception as exc:  # pragma: no cover - exercised by subprocess tests.
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def validate_command(args: argparse.Namespace) -> None:
    """Validate a native problem JSON file."""

    problem = load_problem_json(args.spec)
    summary = {
        "status": "valid",
        "domain": "binary",
        "n_vars": problem.domain.n_vars,
        "linear_rows": problem.linear_csr.n_rows,
        "linear_nnz": problem.linear_csr.nnz,
    }
    _print_json(summary)


def inspect_ctir_command(args: argparse.Namespace) -> None:
    """Print a compact CTIR summary."""

    problem = load_problem_json(args.spec)
    ctir = lower_problem_to_ctir(problem, batch_size=args.batch_size)
    _print_json(inspect_ctir(ctir))


def run_command(args: argparse.Namespace) -> None:
    """Run a native problem through a backend runtime."""

    if args.backend != "cpu":
        raise ValueError(f"unsupported backend: {args.backend}")
    config = RuntimeConfig(
        max_iters=args.max_iters,
        batch_size=args.batch_size,
        seed=args.seed,
        penalty_weight=args.penalty_weight,
    )
    result = run_repair_from_json(args.spec, config=config)
    rows = ledger_to_dicts(result.ledger)
    output = {
        "backend": "cpu",
        "best_state": list(result.best_state),
        "best_objective": result.best_objective,
        "best_penalty": result.best_penalty,
        "feasible": result.best_penalty == 0.0,
        "ledger": rows,
    }

    ledger_path = Path(args.ledger_out)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    report = {
        "status": "ok",
        "backend": "cpu",
        "ledger": str(ledger_path),
        "best_state": list(result.best_state),
        "best_objective": result.best_objective,
        "best_penalty": result.best_penalty,
        "feasible": result.best_penalty == 0.0,
    }
    _print_json(report)


def ledger_command(args: argparse.Namespace) -> None:
    """Print a compact summary for a runtime ledger file."""

    path = Path(args.ledger)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("ledger file must contain a JSON object")
    rows = data.get("ledger")
    if not isinstance(rows, list) or not rows:
        raise ValueError("ledger file must contain a nonempty ledger list")
    last = rows[-1]
    if not isinstance(last, dict):
        raise ValueError("ledger rows must be JSON objects")
    summary = {
        "backend": data.get("backend"),
        "rows": len(rows),
        "best_state": data.get("best_state"),
        "best_objective": data.get("best_objective"),
        "best_penalty": data.get("best_penalty"),
        "feasible": data.get("feasible"),
        "last": {
            "iteration": last.get("iteration"),
            "objective": last.get("objective"),
            "penalty": last.get("penalty"),
            "feasible_count": last.get("feasible_count"),
            "active_violation_count": last.get("active_violation_count"),
        },
    }
    _print_json(summary)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apc")
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate = subcommands.add_parser("validate", help="validate a native problem spec")
    validate.add_argument("spec")
    validate.set_defaults(func=validate_command)

    inspect = subcommands.add_parser("inspect-ctir", help="print a compact CTIR summary")
    inspect.add_argument("spec")
    inspect.add_argument("--batch-size", type=int, default=4)
    inspect.set_defaults(func=inspect_ctir_command)

    run = subcommands.add_parser("run", help="run a native problem")
    run.add_argument("spec")
    run.add_argument("--backend", default="cpu", choices=("cpu",))
    run.add_argument("--ledger-out", default="runs/latest/ledger.json")
    run.add_argument("--max-iters", type=int, default=8)
    run.add_argument("--batch-size", type=int, default=4)
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--penalty-weight", type=float, default=10.0)
    run.set_defaults(func=run_command)

    ledger = subcommands.add_parser("ledger", help="summarize a runtime ledger")
    ledger.add_argument("ledger")
    ledger.set_defaults(func=ledger_command)

    return parser


def _print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
