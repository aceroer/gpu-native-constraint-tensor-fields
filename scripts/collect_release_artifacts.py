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
DEFAULT_HANDOFF_FIXTURES = Path("/tmp/apc-handoff-fixtures.json")
REQUIRED_DOCS = (
    "README.md",
    "ROADMAP.md",
    "docs/QUICKSTART.md",
    "docs/PUBLIC_HANDOFF.md",
    "docs/VERIFY_RELEASE.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/RELEASE_NOTES_DRAFT.md",
    "docs/RELEASE_ARTIFACTS.md",
    "docs/TAG_PREP.md",
    "docs/TAG_EXECUTION.md",
    "docs/RELEASE_ARCHIVE.md",
    "docs/CROSS_PROJECT_HANDOFF.md",
    "docs/CHECKED_HANDOFF_DEMO.md",
    "docs/MAINTENANCE_RELEASES.md",
    "docs/RUNTIME_CONTRACT.md",
    "docs/CUDA_OPERATOR_PARITY.md",
    "native/include/apc_runtime.hpp",
    "native/src/cpu_operator_shim.cpp",
    "scripts/probe_native_host.py",
    "LICENSE",
    "NOTICE",
    "CITATION.cff",
    "docs/ORIGIN.md",
)
REQUIRED_TESTS = (
    "tests/test_release_verifier.py",
    "tests/test_release_checklist.py",
    "tests/test_release_artifacts.py",
    "tests/test_tag_prep.py",
    "tests/test_tag_execution.py",
    "tests/test_release_archive.py",
    "tests/test_cross_project_handoff.py",
    "tests/test_checked_handoff_demo.py",
    "tests/test_checked_handoff_fixtures.py",
    "tests/test_problem_family_handoff_fixture.py",
    "tests/test_handoff_fixture_index.py",
    "tests/test_handoff_fixture_listing.py",
    "tests/test_release_artifact_reader.py",
    "tests/test_release_evidence_smoke.py",
    "tests/test_maintenance_releases.py",
    "tests/test_runtime_contract.py",
    "tests/test_operator_call_ledger.py",
    "tests/test_runtime_status.py",
    "tests/test_native_host_abi.py",
    "tests/test_native_cpu_operator_shim.py",
    "tests/test_native_binding_probe.py",
    "tests/cuda/test_linear_csr_eval.py",
)
REQUIRED_EXAMPLES = (
    "examples/handoff/README.md",
    "examples/handoff/vagent_apc_handoff_report.v1.json",
    "examples/handoff/apc_handoff_check.v1.json",
    "examples/handoff/apc_checked_handoff_demo.v1.json",
    "examples/handoff/vagent_binary_milp_handoff_report.v1.json",
    "examples/handoff/apc_binary_milp_handoff_check.v1.json",
    "examples/handoff/apc_binary_milp_checked_handoff_demo.v1.json",
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
    parser.add_argument(
        "--handoff-fixtures",
        default=str(DEFAULT_HANDOFF_FIXTURES),
        help="handoff fixture listing JSON path",
    )
    parser.add_argument("--out", help="optional JSON output path")
    args = parser.parse_args(argv)

    report = collect_release_artifacts(
        tag=args.tag,
        verify_path=Path(args.verify),
        bench_path=Path(args.bench),
        vector_bench_path=Path(args.vector_bench),
        handoff_fixtures_path=Path(args.handoff_fixtures),
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
    handoff_fixtures_path: Path = DEFAULT_HANDOFF_FIXTURES,
) -> dict[str, Any]:
    """Return a JSON-ready release evidence report."""

    artifacts = {
        "verifier": _load_json_artifact(verify_path),
        "cpu_benchmark": _load_json_artifact(bench_path),
        "vector_demo_benchmark": _load_json_artifact(vector_bench_path),
        "handoff_fixture_listing": _load_json_artifact(handoff_fixtures_path),
    }
    docs = [_file_status(ROOT / relpath, relpath) for relpath in REQUIRED_DOCS]
    tests = [_file_status(ROOT / relpath, relpath) for relpath in REQUIRED_TESTS]
    examples = [_json_file_status(ROOT / relpath, relpath) for relpath in REQUIRED_EXAMPLES]
    checks = _checks(artifacts=artifacts, docs=docs, tests=tests, examples=examples)
    status = "ok" if all(check["ok"] for check in checks) else "failed"
    return {
        "schema": "apc.release_artifacts.v1",
        "status": status,
        "tag": tag,
        "commit": _git_commit(),
        "artifacts": artifacts,
        "docs": docs,
        "tests": tests,
        "examples": examples,
        "checks": checks,
    }


def _checks(
    *,
    artifacts: dict[str, dict[str, Any]],
    docs: list[dict[str, Any]],
    tests: list[dict[str, Any]],
    examples: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    verifier = artifacts["verifier"]
    cpu_benchmark = artifacts["cpu_benchmark"]
    vector_benchmark = artifacts["vector_demo_benchmark"]
    handoff_fixtures = artifacts["handoff_fixture_listing"]
    handoff_payload = _payload(handoff_fixtures)
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
        _check(
            "handoff_fixture_listing_schema",
            handoff_payload.get("schema") == "apc.handoff_fixture_index.v1",
        ),
        _check(
            "handoff_fixture_listing_status",
            handoff_payload.get("status") == "ok",
        ),
        _check("docs_present", all(item["exists"] for item in docs)),
        _check("tests_present", all(item["exists"] for item in tests)),
        _check("examples_present", all(item["exists"] for item in examples)),
        _check("handoff_fixture_schemas", _handoff_fixture_schemas_ok(examples)),
    ]


def _check(name: str, ok: bool) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok)}


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload")
    return payload if isinstance(payload, dict) else {}


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


def _json_file_status(path: Path, relpath: str) -> dict[str, Any]:
    status = _file_status(path, relpath)
    if path.suffix != ".json":
        status["schema"] = None
        return status
    if not path.exists():
        status["schema"] = None
        return status
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        status["schema"] = None
        return status
    status["schema"] = payload.get("schema") if isinstance(payload, dict) else None
    return status


def _handoff_fixture_schemas_ok(examples: list[dict[str, Any]]) -> bool:
    expected = {
        "examples/handoff/README.md": None,
        "examples/handoff/vagent_apc_handoff_report.v1.json": "vagent.apc_handoff_report.v1",
        "examples/handoff/apc_handoff_check.v1.json": "apc.cross_project_handoff_check.v1",
        "examples/handoff/apc_checked_handoff_demo.v1.json": "apc.checked_handoff_runtime_demo.v1",
        "examples/handoff/vagent_binary_milp_handoff_report.v1.json": "vagent.apc_handoff_report.v1",
        "examples/handoff/apc_binary_milp_handoff_check.v1.json": "apc.cross_project_handoff_check.v1",
        "examples/handoff/apc_binary_milp_checked_handoff_demo.v1.json": "apc.checked_handoff_runtime_demo.v1",
    }
    observed = {item["path"]: item.get("schema") for item in examples}
    return observed == expected


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
