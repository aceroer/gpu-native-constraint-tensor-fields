#!/usr/bin/env python3
"""Verify the public release surface."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    name: str
    cmd: list[str]
    env: dict[str, str] | None = None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="verify_public_release.py")
    parser.add_argument("--full", action="store_true", help="run the full unittest suite")
    parser.add_argument("--out", help="optional JSON output path")
    args = parser.parse_args(argv)

    report = run_verification(full=args.full)
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "ok" else 1


def run_verification(*, full: bool = False) -> dict[str, Any]:
    """Run release checks and return a JSON-ready report."""

    checks = _checks(full=full)
    results = [_run_check(check) for check in checks]
    status = "ok" if all(result["returncode"] == 0 for result in results) else "failed"
    return {
        "schema": "apc.public_release_verification.v1",
        "status": status,
        "mode": "full" if full else "quick",
        "checks": results,
    }


def _checks(*, full: bool) -> list[Check]:
    py = sys.executable
    env = _env("src:examples/binary_milp_repair:examples/vector_state_repair")
    quick_env = _env("src:examples/vector_state_repair")
    checks = [
        Check("compileall", [py, "-m", "compileall", "src", "tests", "scripts", "examples/vector_state_repair"]),
        Check(
            "quickstart",
            [py, "-m", "unittest", "tests.test_quickstart", "-v"],
            env=quick_env,
        ),
        Check(
            "public_docs",
            [py, "-m", "unittest", "tests.test_public_docs", "-v"],
            env=_env("src"),
        ),
        Check(
            "vagent_handoff_consumer",
            [py, "-m", "unittest", "tests.test_vagent_handoff_consumer", "-v"],
            env=_env("src"),
        ),
        Check(
            "checked_handoff_demo",
            [py, "-m", "unittest", "tests.test_checked_handoff_demo", "-v"],
            env=_env("src:."),
        ),
        Check(
            "checked_handoff_fixtures",
            [py, "-m", "unittest", "tests.test_checked_handoff_fixtures", "-v"],
            env=_env("src:."),
        ),
        Check(
            "cpu_benchmark",
            [
                py,
                "scripts/run_bench.py",
                "examples/specs/binary_milp_tiny.json",
                "--out",
                "/tmp/apc-release-bench.json",
                "--max-iters",
                "2",
            ],
            env=_env("src"),
        ),
        Check(
            "vector_demo_benchmark",
            [
                py,
                "scripts/run_vector_demo_bench.py",
                "examples/specs/binary_milp_tiny.json",
                "--out",
                "/tmp/apc-release-vector-demo-bench.json",
            ],
            env=quick_env,
        ),
        Check(
            "boundary_scan",
            [
                "rg",
                "-n",
                _boundary_pattern(),
                ".",
                "--glob",
                "!/.git/**",
            ],
        ),
    ]
    if full:
        checks.insert(
            0,
            Check(
                "unittest",
                [py, "-m", "unittest", "discover", "-s", "tests", "-v"],
                env=env,
            ),
        )
    return checks


def _run_check(check: Check) -> dict[str, Any]:
    env = os.environ.copy()
    if check.env:
        env.update(check.env)
    completed = subprocess.run(
        check.cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    returncode = _normalize_returncode(check, completed.returncode)
    return {
        "name": check.name,
        "cmd": check.cmd,
        "returncode": returncode,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
    }


def _normalize_returncode(check: Check, returncode: int) -> int:
    if check.name == "boundary_scan" and returncode == 1:
        return 0
    return returncode


def _env(pythonpath: str) -> dict[str, str]:
    return {"PYTHONPATH": pythonpath}


def _boundary_pattern() -> str:
    terms = (
        "INTER" + "NAL",
        "internal" + "_layers",
        "Local" + "/private",
        "场" + "代数",
        "Max" + "well",
        "电路" + "模块",
        "母" + "理论",
        "内部" + "组装",
        "成熟" + "读数",
    )
    return "|".join(terms)


if __name__ == "__main__":
    raise SystemExit(main())
