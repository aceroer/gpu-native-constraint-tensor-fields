#!/usr/bin/env python3
"""Check a vAgentRT APC handoff report against APC public shapes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from apc.adapters.vagent_handoff import check_vagent_handoff_file, write_handoff_check


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="check_vagent_handoff.py")
    parser.add_argument("handoff", help="Path to vagent.apc_handoff_report.v1 JSON")
    parser.add_argument("--out", default=None, help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = check_vagent_handoff_file(args.handoff)
    if args.out:
        write_handoff_check(report, args.out)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
