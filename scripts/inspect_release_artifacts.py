#!/usr/bin/env python3
"""Summarize a public release artifact report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACTS = Path("/tmp/apc-release-artifacts.json")
RELEASE_SCHEMA = "apc.release_artifacts.v1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="inspect_release_artifacts.py")
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_ARTIFACTS),
        help="release artifact JSON path",
    )
    parser.add_argument("--out", help="optional summary JSON output path")
    args = parser.parse_args(argv)

    summary = inspect_release_artifacts(Path(args.path))
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] != "failed" else 1


def inspect_release_artifacts(path: Path) -> dict[str, Any]:
    """Return a compact factual summary for an apc.release_artifacts.v1 file."""

    artifact = _load_json(path)
    if artifact is None:
        return _failed_summary(path=path, reason="missing_or_invalid_json")
    if artifact.get("schema") != RELEASE_SCHEMA:
        return _failed_summary(
            path=path,
            reason="unsupported_schema",
            observed_schema=_string_or_none(artifact.get("schema")),
        )

    artifacts = artifact.get("artifacts")
    artifact_summaries = _artifact_summaries(artifacts if isinstance(artifacts, dict) else {})
    handoff = artifact_summaries.get("handoff_fixture_listing", {})
    return {
        "schema": "apc.release_artifacts_summary.v1",
        "source_schema": RELEASE_SCHEMA,
        "source_path": str(path),
        "status": _string_or_value(artifact.get("status"), default="unknown"),
        "tag": _string_or_value(artifact.get("tag"), default="untagged"),
        "commit": _string_or_value(artifact.get("commit"), default="unknown"),
        "artifact_count": len(artifact_summaries),
        "artifact_schemas": artifact_summaries,
        "fixture_count": _fixture_count(handoff),
        "check_count": _count_items(artifact.get("checks")),
        "failed_checks": _failed_check_names(artifact.get("checks")),
        "notes": [
            "Summary is factual release evidence inspection only.",
            "No release quality or compatibility claim is inferred from this summary.",
        ],
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _failed_summary(
    *,
    path: Path,
    reason: str,
    observed_schema: str | None = None,
) -> dict[str, Any]:
    summary = {
        "schema": "apc.release_artifacts_summary.v1",
        "source_schema": observed_schema,
        "source_path": str(path),
        "status": "failed",
        "reason": reason,
        "tag": "unknown",
        "commit": "unknown",
        "artifact_count": 0,
        "artifact_schemas": {},
        "fixture_count": 0,
        "check_count": 0,
        "failed_checks": [],
        "notes": [
            "Summary is factual release evidence inspection only.",
            "No release quality or compatibility claim is inferred from this summary.",
        ],
    }
    return summary


def _artifact_summaries(artifacts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for name, artifact in sorted(artifacts.items()):
        if not isinstance(artifact, dict):
            summaries[name] = {
                "exists": False,
                "schema": None,
                "fixture_count": None,
            }
            continue
        payload = artifact.get("payload")
        summaries[name] = {
            "exists": bool(artifact.get("exists")),
            "schema": _string_or_none(artifact.get("schema")),
            "fixture_count": _payload_fixture_count(payload),
        }
    return summaries


def _payload_fixture_count(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get("fixture_count")
    if isinstance(value, int) and value >= 0:
        return value
    return None


def _fixture_count(handoff_summary: dict[str, Any]) -> int:
    value = handoff_summary.get("fixture_count")
    return value if isinstance(value, int) and value >= 0 else 0


def _failed_check_names(checks: Any) -> list[str]:
    if not isinstance(checks, list):
        return []
    names: list[str] = []
    for check in checks:
        if not isinstance(check, dict):
            continue
        if check.get("ok") is True:
            continue
        name = check.get("name")
        names.append(name if isinstance(name, str) else "unnamed_check")
    return names


def _count_items(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _string_or_value(value: Any, *, default: str) -> str:
    return value if isinstance(value, str) else default


if __name__ == "__main__":
    raise SystemExit(main())
