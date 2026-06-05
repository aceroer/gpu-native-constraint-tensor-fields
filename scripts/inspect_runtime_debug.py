#!/usr/bin/env python3
"""Write a public runtime debug report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from apc.debug import inspect_runtime_debug


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="inspect_runtime_debug.py")
    parser.add_argument("spec")
    parser.add_argument("--ledger")
    parser.add_argument("--artifact-dir")
    parser.add_argument("--release-artifacts")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--out")
    args = parser.parse_args(argv)

    report = inspect_runtime_debug(
        spec=args.spec,
        ledger=args.ledger,
        artifact_dir=args.artifact_dir,
        release_artifacts=args.release_artifacts,
        batch_size=args.batch_size,
    )
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
