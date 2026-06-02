"""Consumer for vAgentRT public APC handoff JSON reports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..branch_tensor import BranchRoute, BranchTensor, branch_tensor_summary
from ..ctir import StateBatch
from ..interface_projection import (
    InterfaceProjection,
    interface_projection_to_dict,
    project_public_summary,
)
from ..state_pool import StatePool, state_pool_summary


SOURCE_REPORT_SCHEMA = "vagent.apc_handoff_report.v1"
SOURCE_ARTIFACT_SCHEMA = "vagent.apc_handoff.v1"
CHECK_SCHEMA = "apc.cross_project_handoff_check.v1"


@dataclass(frozen=True)
class VAgentHandoffMaterialization:
    """APC-side materialization of one vAgentRT handoff artifact."""

    task_id: str
    state_pool: StatePool
    branch_tensor: BranchTensor
    reduction_gate: dict[str, Any]
    interface_projection: InterfaceProjection
    source: dict[str, Any]


def load_vagent_handoff_report(path: str | Path) -> dict[str, Any]:
    """Load a vAgentRT handoff JSON report from disk."""

    with Path(path).open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    if not isinstance(report, dict):
        raise ValueError("vAgentRT handoff report must be a JSON object")
    return report


def check_vagent_handoff_report(report: dict[str, Any]) -> dict[str, Any]:
    """Validate and project a vAgentRT handoff report into APC public shapes."""

    if report.get("schema") != SOURCE_REPORT_SCHEMA:
        raise ValueError(f"expected schema {SOURCE_REPORT_SCHEMA}")
    artifacts = _list(report, "artifacts")
    if not artifacts:
        raise ValueError("artifacts must not be empty")

    materialized = [_materialize_artifact(artifact) for artifact in artifacts]
    task_ids = [item.task_id for item in materialized]
    expected_task_count = _int(report, "task_count")
    if expected_task_count != len(materialized):
        raise ValueError("task_count must equal artifact count")

    return {
        "schema": CHECK_SCHEMA,
        "status": "ok",
        "source_schema": SOURCE_REPORT_SCHEMA,
        "task_count": len(materialized),
        "task_ids": task_ids,
        "runtime_path": [
            "vAgentRT handoff JSON",
            "StatePool",
            "BranchTensor",
            "ReductionGate",
            "InterfaceProjection",
        ],
        "artifacts": [_materialization_to_dict(item) for item in materialized],
        "notes": [
            "This consumer reads JSON only and does not import vAgentRT.",
            "This is a cross-project handoff check, not a drop-in compatibility claim.",
        ],
    }


def check_vagent_handoff_file(path: str | Path) -> dict[str, Any]:
    """Load and check a vAgentRT handoff report file."""

    return check_vagent_handoff_report(load_vagent_handoff_report(path))


def write_handoff_check(report: dict[str, Any], path: str | Path) -> None:
    """Write a handoff check report as stable JSON."""

    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _materialize_artifact(artifact: Any) -> VAgentHandoffMaterialization:
    if not isinstance(artifact, dict):
        raise ValueError("handoff artifact must be an object")
    if artifact.get("schema") != SOURCE_ARTIFACT_SCHEMA:
        raise ValueError(f"expected artifact schema {SOURCE_ARTIFACT_SCHEMA}")

    source = _object(artifact, "source")
    task_id = _str(source, "task_id")
    pool = _materialize_state_pool(_object(artifact, "state_pool"))
    tensor = _materialize_branch_tensor(_object(artifact, "branch_tensor"))
    if tensor.batch_size != pool.batch_size:
        raise ValueError("BranchTensor batch size must match StatePool")

    reduction_gate = _validate_reduction_gate(_object(artifact, "reduction_gate"), tensor)
    projection = _materialize_interface_projection(
        _object(artifact, "interface_projection"),
        task_id=task_id,
        selected_count=reduction_gate["selected_count"],
    )
    return VAgentHandoffMaterialization(
        task_id=task_id,
        state_pool=pool,
        branch_tensor=tensor,
        reduction_gate=reduction_gate,
        interface_projection=projection,
        source=dict(source),
    )


def _materialize_state_pool(data: dict[str, Any]) -> StatePool:
    batch_size = _int(data, "batch_size")
    n_vars = _int(data, "n_vars")
    scores = _number_tuple(data, "scores")
    uncertainty = _number_tuple(data, "uncertainty")
    alive_mask = _bool_tuple(data, "alive_mask")
    metadata = _dict_tuple(data, "metadata")
    if len(scores) != batch_size:
        raise ValueError("state_pool.scores length must equal batch_size")
    if len(uncertainty) != batch_size:
        raise ValueError("state_pool.uncertainty length must equal batch_size")
    if len(alive_mask) != batch_size:
        raise ValueError("state_pool.alive_mask length must equal batch_size")
    if len(metadata) != batch_size:
        raise ValueError("state_pool.metadata length must equal batch_size")
    rows = tuple(_synthetic_state_row(index, n_vars) for index in range(batch_size))
    return StatePool(
        states=StateBatch(rows),
        scores=scores,
        uncertainty=uncertainty,
        alive_mask=alive_mask,
        metadata=metadata,
    )


def _synthetic_state_row(index: int, n_vars: int) -> tuple[int, ...]:
    if n_vars <= 0:
        raise ValueError("state_pool.n_vars must be positive")
    return tuple(1 if col == index % n_vars else 0 for col in range(n_vars))


def _materialize_branch_tensor(data: dict[str, Any]) -> BranchTensor:
    shape = _int_list(data, "shape")
    if len(shape) != 2:
        raise ValueError("branch_tensor.shape must have two dimensions")
    routes_data = _list(data, "routes")
    if len(routes_data) != shape[0]:
        raise ValueError("branch_tensor.routes outer length must match shape")

    routes: list[tuple[BranchRoute, ...]] = []
    alive_rows: list[tuple[bool, ...]] = []
    metadata_rows: list[tuple[dict[str, Any], ...]] = []
    for state_index, row_data in enumerate(routes_data):
        if not isinstance(row_data, list):
            raise ValueError("branch_tensor.routes rows must be lists")
        if len(row_data) != shape[1]:
            raise ValueError("branch_tensor.routes row length must match shape")
        route_row: list[BranchRoute] = []
        alive_row: list[bool] = []
        meta_row: list[dict[str, Any]] = []
        for route_index, route_data in enumerate(row_data):
            route = _object_value(route_data, "branch route")
            canonical_key = _canonical_key(route)
            route_row.append(
                BranchRoute(
                    state_index=_int(route, "state_index"),
                    route_index=_int(route, "route_index"),
                    move_type=_str(route, "move_type"),
                    payload=tuple(_int_list(route, "payload")),
                    canonical_key=canonical_key,
                )
            )
            alive_row.append(_bool(route, "alive"))
            meta_row.append(
                {
                    "source": "vagent.apc_handoff.v1",
                    "action": route.get("action"),
                    "branch_id": route.get("branch_id"),
                }
            )
        routes.append(tuple(route_row))
        alive_rows.append(tuple(alive_row))
        metadata_rows.append(tuple(meta_row))
    return BranchTensor(
        routes=tuple(routes),
        alive_mask=tuple(alive_rows),
        metadata=tuple(metadata_rows),
    )


def _canonical_key(route: dict[str, Any]) -> tuple[str, tuple[int, ...]]:
    value = route.get("canonical_key")
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not isinstance(value[0], str)
        or not isinstance(value[1], list)
        or not all(isinstance(item, int) for item in value[1])
    ):
        raise ValueError("branch route canonical_key must be [kind, payload]")
    return (value[0], tuple(value[1]))


def _validate_reduction_gate(data: dict[str, Any], tensor: BranchTensor) -> dict[str, Any]:
    selected = _list(data, "selected")
    selected_refs = []
    for item in selected:
        row = _object_value(item, "selected route")
        state_index = _int(row, "state_index")
        route_index = _int(row, "route_index")
        if state_index < 0 or state_index >= tensor.batch_size:
            raise ValueError("selected route state_index out of range")
        if route_index < 0 or route_index >= tensor.routes_per_state:
            raise ValueError("selected route route_index out of range")
        selected_refs.append(
            {
                "rank": _int(row, "rank"),
                "state_index": state_index,
                "route_index": route_index,
                "move_type": _str(row, "move_type"),
                "payload": _int_list(row, "payload"),
                "score": _number(row, "score"),
                "uncertainty": _number(row, "uncertainty"),
                "reduced_score": _number(row, "reduced_score"),
                "energy": _number(row, "energy"),
            }
        )

    selected_count = _int(data, "selected_count")
    if selected_count != len(selected_refs):
        raise ValueError("reduction_gate.selected_count must equal selected length")
    return {
        "top_k": _int(data, "top_k"),
        "before_count": _int(data, "before_count"),
        "after_count": _int(data, "after_count"),
        "selected_count": selected_count,
        "branch_efficiency": _number(data, "branch_efficiency"),
        "selected": selected_refs,
    }


def _materialize_interface_projection(
    data: dict[str, Any],
    *,
    task_id: str,
    selected_count: int,
) -> InterfaceProjection:
    projection = _object(data, "projection")
    payload = _object(data, "payload")
    if _str(payload, "task_id") != task_id:
        raise ValueError("interface_projection.payload.task_id must match source.task_id")
    if _int(payload, "selected_count") != selected_count:
        raise ValueError("interface_projection selected_count must match reduction gate")
    return project_public_summary(
        _str(projection, "kind"),
        dict(payload),
        reason=_str(projection, "reason"),
    )


def _materialization_to_dict(item: VAgentHandoffMaterialization) -> dict[str, Any]:
    return {
        "task_id": item.task_id,
        "source": dict(item.source),
        "state_pool": state_pool_summary(item.state_pool),
        "branch_tensor": branch_tensor_summary(item.branch_tensor),
        "reduction_gate": item.reduction_gate,
        "interface_projection": interface_projection_to_dict(item.interface_projection),
        "checks": {
            "state_pool_shape": "ok",
            "branch_tensor_shape": "ok",
            "reduction_gate_refs": "ok",
            "interface_projection": "ok",
        },
    }


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


def _bool(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
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


def _number_tuple(data: dict[str, Any], key: str) -> tuple[float, ...]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list of numbers")
    return tuple(_number({"value": item}, "value") for item in value)


def _bool_tuple(data: dict[str, Any], key: str) -> tuple[bool, ...]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, bool) for item in value):
        raise ValueError(f"{key} must be a list of booleans")
    return tuple(value)


def _dict_tuple(data: dict[str, Any], key: str) -> tuple[dict[str, Any], ...]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{key} must be a list of objects")
    return tuple(dict(item) for item in value)
