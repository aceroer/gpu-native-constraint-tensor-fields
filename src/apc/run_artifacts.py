"""Stable run artifact writer for public runtime evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RUN_ARTIFACT_SCHEMA = "apc.run_artifacts.v1"
TIMING_FIELDS = (
    "kernel_time_s",
    "copy_time_s",
    "layout_conversion_time_s",
    "end_to_end_time_s",
)


def write_run_artifacts(
    *,
    report: dict[str, Any],
    source_spec: str | Path,
    artifact_dir: str | Path,
    run_id: str = "latest",
) -> dict[str, Any]:
    """Write deterministic public run artifacts and return a manifest."""

    root = Path(artifact_dir) / run_id
    root.mkdir(parents=True, exist_ok=True)
    spec_payload = _load_json(Path(source_spec))
    result_payload = _sanitize_paths(report)
    ledger_payload = _ledger_payload(result_payload)
    timing_payload = _timing_payload(result_payload)
    metadata_payload = {
        "schema": RUN_ARTIFACT_SCHEMA,
        "run_id": run_id,
        "problem_family": _string_or_unknown(result_payload.get("problem_family")),
        "backend": _string_or_unknown(result_payload.get("backend")),
        "status": _string_or_unknown(result_payload.get("status")),
        "source_spec_name": Path(source_spec).name,
        "files": {
            "input": "input.json",
            "result": "result.json",
            "ledger": "ledger.json",
            "timings": "timings.json",
            "metadata": "metadata.json",
        },
    }

    _write_json(root / "input.json", spec_payload)
    _write_json(root / "result.json", result_payload)
    _write_json(root / "ledger.json", ledger_payload)
    _write_json(root / "timings.json", timing_payload)
    _write_json(root / "metadata.json", metadata_payload)
    return {
        **metadata_payload,
        "artifact_dir": str(root),
    }


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ledger_payload(report: dict[str, Any]) -> dict[str, Any]:
    ledger = report.get("ledger")
    return {
        "schema": "apc.run_artifact_ledger.v1",
        "problem_family": _string_or_unknown(report.get("problem_family")),
        "backend": _string_or_unknown(report.get("backend")),
        "status": _string_or_unknown(report.get("status")),
        "ledger": ledger if isinstance(ledger, list) else [],
    }


def _timing_payload(report: dict[str, Any]) -> dict[str, Any]:
    timing = report.get("timing")
    if not isinstance(timing, dict):
        timing = {}
    return {
        "schema": "apc.run_artifact_timings.v1",
        "problem_family": _string_or_unknown(report.get("problem_family")),
        "backend": _string_or_unknown(report.get("backend")),
        "status": _string_or_unknown(report.get("status")),
        "timing": {
            field: _number_or_none(timing.get(field))
            for field in TIMING_FIELDS
        },
    }


def _sanitize_paths(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if isinstance(item, str) and _looks_like_path_key(key):
                sanitized[key] = Path(item).name if Path(item).is_absolute() else item
            else:
                sanitized[key] = _sanitize_paths(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_paths(item) for item in value]
    return value


def _looks_like_path_key(key: str) -> bool:
    lowered = key.lower()
    return lowered == "path" or lowered.endswith("_path") or lowered.endswith("_report")


def _string_or_unknown(value: Any) -> str:
    return value if isinstance(value, str) else "unknown"


def _number_or_none(value: Any) -> float | int | None:
    return value if isinstance(value, (float, int)) and not isinstance(value, bool) else None
