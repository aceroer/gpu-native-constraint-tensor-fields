#!/usr/bin/env python3
"""Run the public release evidence route end to end."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("/tmp")
DEFAULT_BENCH = Path("/tmp/apc-release-bench.json")
DEFAULT_VECTOR_BENCH = Path("/tmp/apc-release-vector-demo-bench.json")
DEFAULT_HANDOFF_FIXTURES = Path("/tmp/apc-handoff-fixtures.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="smoke_release_evidence.py")
    parser.add_argument("--tag", default="v0.1.0-alpha.0", help="tag name or candidate tag")
    parser.add_argument("--full", action="store_true", help="run the full release verifier")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="directory for verifier, artifact, and summary reports",
    )
    parser.add_argument("--out", help="optional smoke report JSON output path")
    args = parser.parse_args(argv)

    report = run_release_evidence_smoke(
        tag=args.tag,
        output_dir=Path(args.output_dir),
        full=args.full,
    )
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "ok" else 1


def run_release_evidence_smoke(
    *,
    tag: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    full: bool = False,
) -> dict[str, Any]:
    """Run verifier, collector, and reader as a factual evidence smoke route."""

    output_dir.mkdir(parents=True, exist_ok=True)
    verify_path = output_dir / ("apc-release-verify-full.json" if full else "apc-release-verify.json")
    artifacts_path = output_dir / "apc-release-artifacts.json"
    summary_path = output_dir / "apc-release-artifacts-summary.json"

    steps: list[dict[str, Any]] = []
    verifier_cmd = [
        sys.executable,
        "scripts/verify_public_release.py",
        "--out",
        str(verify_path),
    ]
    if full:
        verifier_cmd.insert(2, "--full")
    steps.append(_run_step("verifier", verifier_cmd, verify_path))

    if _steps_ok(steps):
        collector_cmd = [
            sys.executable,
            "scripts/collect_release_artifacts.py",
            "--tag",
            tag,
            "--verify",
            str(verify_path),
            "--bench",
            str(DEFAULT_BENCH),
            "--vector-bench",
            str(DEFAULT_VECTOR_BENCH),
            "--handoff-fixtures",
            str(DEFAULT_HANDOFF_FIXTURES),
            "--out",
            str(artifacts_path),
        ]
        steps.append(_run_step("collector", collector_cmd, artifacts_path))
    else:
        steps.append(_skipped_step("collector", artifacts_path))

    if _steps_ok(steps):
        reader_cmd = [
            sys.executable,
            "scripts/inspect_release_artifacts.py",
            str(artifacts_path),
            "--out",
            str(summary_path),
        ]
        steps.append(_run_step("reader", reader_cmd, summary_path))
    else:
        steps.append(_skipped_step("reader", summary_path))

    return {
        "schema": "apc.release_evidence_smoke.v1",
        "status": "ok" if _steps_ok(steps) else "failed",
        "tag": tag,
        "mode": "full" if full else "quick",
        "paths": {
            "verifier": str(verify_path),
            "collector": str(artifacts_path),
            "reader": str(summary_path),
        },
        "steps": steps,
        "notes": [
            "Smoke command runs factual release evidence steps only.",
            "No release quality or compatibility claim is inferred from this smoke report.",
        ],
    }


def _run_step(name: str, cmd: list[str], output_path: Path) -> dict[str, Any]:
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": name,
        "cmd": cmd,
        "output_path": str(output_path),
        "output_exists": output_path.exists(),
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
    }


def _skipped_step(name: str, output_path: Path) -> dict[str, Any]:
    return {
        "name": name,
        "cmd": [],
        "output_path": str(output_path),
        "output_exists": output_path.exists(),
        "returncode": None,
        "skipped": True,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def _steps_ok(steps: list[dict[str, Any]]) -> bool:
    return all(step.get("returncode") == 0 for step in steps)


if __name__ == "__main__":
    raise SystemExit(main())
