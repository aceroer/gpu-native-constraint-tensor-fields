#!/usr/bin/env python3
"""Collect public release evidence into one JSON artifact."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


DEFAULT_VERIFY = Path("/tmp/apc-release-verify.json")
DEFAULT_BENCH = Path("/tmp/apc-release-bench.json")
DEFAULT_VECTOR_BENCH = Path("/tmp/apc-release-vector-demo-bench.json")
REQUIRED_DOCS = (
    "README.md",
    "ROADMAP.md",
    "docs/QUICKSTART.md",
    "docs/PUBLIC_HANDOFF.md",
    "docs/VERIFY_RELEASE.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/RELEASE_NOTES_DRAFT.md",
    "docs/RELEASE_ARTIFACTS.md",
    "LICENSE",
    "NOTICE",
    "CITATION.cff",
    "docs/ORIGIN.md",
)
REQUIRED_TESTS = (
    "tests/test_release_verifier.py",
    "tests/test_release_checklist.py",
    "tests/test_release_artifacts.py",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="collect_release_artifacts.py")
    parser.add_argument("--tag", default="untagged", help="tag name or candidate tag")
    parser.add_argument("--verify", default=str(DEFAULT_VERIFY), help="release verifier JSON path")
    parser.add_argument("--bench", default=str(DEFAULT_BENCH), help="CPU benchmark JSON path")
    parser.add_argument(
        "--vector-bench",
        default=str(DEFAULT_VECTOR_BENCH),
        help="vector-native demo benchmark JSON path",
    )
    parser.add_argument("--out", help="optional JSON output path")
    args = parser.parse_args(argv)

    report = collect_release_artifacts(
        tag=args.tag,
        verify_path=Path(args.verify),
        bench_path=Path(args.bench),
        vector_bench_path=Path(args.vector_bench),
    )
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "ok" else 1


def collect_release_artifacts(
    *,
    tag: str,
    verify_path: Path,
    bench_path: Path,
    vector_bench_path: Path,
) -> dict[str, Any]:
    """Return a JSON-ready release evidence report."""

    artifacts = {
        "verifier": _load_json_artifact(verify_path),
        "cpu_benchmark": _load_json_artifact(bench_path),
        "vector_demo_benchmark": _load_json_artifact(vector_bench_path),
    }
    docs = [_file_status(ROOT / relpath, relpath) for relpath in REQUIRED_DOCS]
    tests = [_file_status(ROOT / relpath, relpath) for relpath in REQUIRED_TESTS]
    checks = _checks(artifacts=artifacts, docs=docs, tests=tests)
    status = "ok" if all(check["ok"] for check in checks) else "failed"
    return {
        "schema": "apc.release_artifacts.v1",
        "status": status,
        "tag": tag,
        "commit": _git_commit(),
        "artifacts": artifacts,
        "docs": docs,
        "tests": tests,
        "checks": checks,
    }


def _checks(
    *,
    artifacts: dict[str, dict[str, Any]],
    docs: list[dict[str, Any]],
    tests: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    verifier = artifacts["verifier"]
    cpu_benchmark = artifacts["cpu_benchmark"]
    vector_benchmark = artifacts["vector_demo_benchmark"]
    return [
        _check(
            "verifier_schema",
            verifier.get("payload", {}).get("schema") == "apc.public_release_verification.v1",
        ),
        _check("verifier_status", verifier.get("payload", {}).get("status") == "ok"),
        _check("cpu_benchmark_schema", cpu_benchmark.get("payload", {}).get("schema") == "apc.benchmark.v1"),
        _check(
            "vector_demo_benchmark_schema",
            _vector_demo_benchmark_schema(vector_benchmark) == "apc.vector_demo_benchmark.v1",
        ),
        _check("docs_present", all(item["exists"] for item in docs)),
        _check("tests_present", all(item["exists"] for item in tests)),
    ]


def _check(name: str, ok: bool) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok)}


def _load_json_artifact(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.exists():
        return {
            "path": str(path),
            "exists": False,
            "schema": None,
            "payload": None,
        }
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "path": str(path),
            "exists": True,
            "schema": None,
            "payload": None,
            "error": str(exc),
        }
    return {
        "path": str(path),
        "exists": True,
        "schema": _artifact_schema(payload),
        "payload": payload,
    }


def _artifact_schema(payload: dict[str, Any]) -> str | None:
    if isinstance(payload.get("schema"), str):
        return payload["schema"]
    benchmark = payload.get("payload", {}).get("benchmark", {})
    if isinstance(benchmark.get("schema"), str):
        return benchmark["schema"]
    return None


def _vector_demo_benchmark_schema(artifact: dict[str, Any]) -> str | None:
    payload = artifact.get("payload")
    if not isinstance(payload, dict):
        return None
    demo_payload = payload.get("payload")
    if not isinstance(demo_payload, dict):
        return None
    benchmark = demo_payload.get("benchmark")
    if not isinstance(benchmark, dict):
        return None
    schema = benchmark.get("schema")
    return schema if isinstance(schema, str) else None


def _file_status(path: Path, relpath: str) -> dict[str, Any]:
    return {
        "path": relpath,
        "exists": path.exists(),
    }


def _git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
