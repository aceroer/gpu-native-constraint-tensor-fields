#!/usr/bin/env python3
"""Run a small APC-side demo from a checked cross-project handoff report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CHECK_SCHEMA = "apc.cross_project_handoff_check.v1"
DEMO_SCHEMA = "apc.checked_handoff_runtime_demo.v1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run_checked_handoff_demo.py")
    parser.add_argument("check", help="Path to apc.cross_project_handoff_check.v1 JSON")
    parser.add_argument("--out", default=None, help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = run_checked_handoff_demo_file(args.check)
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def run_checked_handoff_demo_file(path: str | Path) -> dict[str, Any]:
    """Load a checked handoff report and return a demo runtime summary."""

    with Path(path).open("r", encoding="utf-8") as handle:
        check = json.load(handle)
    if not isinstance(check, dict):
        raise ValueError("checked handoff report must be a JSON object")
    return run_checked_handoff_demo(check)


def run_checked_handoff_demo(check: dict[str, Any]) -> dict[str, Any]:
    """Project checked handoff artifacts into a small APC runtime route summary."""

    if check.get("schema") != CHECK_SCHEMA:
        raise ValueError(f"expected schema {CHECK_SCHEMA}")
    if check.get("status") != "ok":
        raise ValueError("checked handoff status must be ok")
    artifacts = _list(check, "artifacts")
    tasks = [_task_summary(artifact) for artifact in artifacts]
    return {
        "schema": DEMO_SCHEMA,
        "status": "ok",
        "source_schema": CHECK_SCHEMA,
        "task_count": len(tasks),
        "runtime_route": [
            "checked handoff JSON",
            "StatePool inspection",
            "selected action summary",
            "InterfaceProjection payload",
        ],
        "tasks": tasks,
        "notes": [
            "This demo consumes a checked handoff report only.",
            "This route is an inspection demo, not a drop-in runtime compatibility claim.",
        ],
    }


def _task_summary(artifact: Any) -> dict[str, Any]:
    artifact = _object_value(artifact, "artifact")
    state_pool = _object(artifact, "state_pool")
    branch_tensor = _object(artifact, "branch_tensor")
    reduction_gate = _object(artifact, "reduction_gate")
    projection = _object(artifact, "interface_projection")
    payload = _object(projection, "payload")
    selected = _list(reduction_gate, "selected")
    selected_actions = _selected_actions(selected=selected, payload=payload)
    scores = _number_list(state_pool, "scores")
    return {
        "task_id": _str(artifact, "task_id"),
        "state_pool": {
            "batch_size": _int(state_pool, "batch_size"),
            "alive_count": _int(state_pool, "alive_count"),
            "score_min": min(scores) if scores else None,
            "score_max": max(scores) if scores else None,
        },
        "branch_tensor": {
            "shape": _int_list(branch_tensor, "shape"),
            "alive_count": _int(branch_tensor, "alive_count"),
        },
        "selected_actions": selected_actions,
        "selected_count": _int(reduction_gate, "selected_count"),
        "branch_efficiency": _number(reduction_gate, "branch_efficiency"),
        "projection_kind": _str(_object(projection, "projection"), "kind"),
        "checks": {
            "state_pool_present": "ok",
            "selected_actions_present": "ok" if selected_actions else "empty",
            "projection_payload_present": "ok",
        },
    }


def _selected_actions(*, selected: list[Any], payload: dict[str, Any]) -> list[str]:
    actions = payload.get("selected_actions")
    if isinstance(actions, list) and all(isinstance(item, str) for item in actions):
        return list(actions)
    values: list[str] = []
    for item in selected:
        route = _object_value(item, "selected route")
        move_type = _str(route, "move_type")
        payload_values = _int_list(route, "payload")
        values.append(f"{move_type}:{','.join(str(value) for value in payload_values)}")
    return values


def _object(data: dict[str, Any], key: str) -> dict[str, Any]:
    return _object_value(data.get(key), key)


def _object_value(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return value


def _str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _number(data: dict[str, Any], key: str) -> float:
    value = data.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"{key} must be a number")
    return float(value)


def _int_list(data: dict[str, Any], key: str) -> list[int]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, int) for item in value):
        raise ValueError(f"{key} must be a list of integers")
    return list(value)


def _number_list(data: dict[str, Any], key: str) -> list[float]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, int | float) for item in value):
        raise ValueError(f"{key} must be a list of numbers")
    return [float(item) for item in value]


if __name__ == "__main__":
    raise SystemExit(main())
