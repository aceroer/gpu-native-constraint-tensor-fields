"""Runnable vector-native repair demo bridge."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apc import (
    ReductionConfig,
    branch_tensor_from_state_pool,
    branch_tensor_summary,
    initialize_state_pool,
    interface_projection_to_dict,
    load_problem_json,
    lower_problem_to_ctir,
    project_runtime_summary,
    reduce_branch_tensor,
    reduction_gate_summary,
    state_pool_summary,
)


def run_vector_state_repair_demo(
    spec_path: str | Path,
    *,
    batch_size: int = 4,
    top_k: int = 2,
    penalty_weight: float = 10.0,
    diversity_weight: float = 0.0,
) -> dict[str, Any]:
    """Run the state-pool to projection demo path and return a public report."""

    problem = load_problem_json(spec_path)
    ctir = lower_problem_to_ctir(problem, batch_size=batch_size)
    pool = initialize_state_pool(ctir)
    tensor = branch_tensor_from_state_pool(ctir, pool)
    reduction = reduce_branch_tensor(
        ctir,
        pool,
        tensor,
        config=ReductionConfig(
            top_k=top_k,
            penalty_weight=penalty_weight,
            diversity_weight=diversity_weight,
        ),
    )
    payload = build_report(
        spec_path=spec_path,
        pool_summary=state_pool_summary(pool),
        branch_summary=branch_tensor_summary(tensor),
        reduction_summary=reduction_gate_summary(reduction),
    )
    projection = project_runtime_summary(
        payload,
        reason="vector-native repair demo projected from state pool, branch tensor, and reduction gate",
    )
    return interface_projection_to_dict(projection)


def build_report(
    *,
    spec_path: str | Path,
    pool_summary: dict[str, Any],
    branch_summary: dict[str, Any],
    reduction_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build a reproducible demo report payload."""

    branch_count = branch_summary["shape"][0] * branch_summary["shape"][1]
    selected_action_count = reduction_summary["selected_count"]
    success = selected_action_count > 0 and branch_summary["alive_count"] > 0
    return {
        "schema": "apc.vector_state_repair_demo.v1",
        "problem": {
            "path": str(spec_path),
            "family": "binary_milp",
        },
        "state_pool": pool_summary,
        "branch_tensor": {
            "shape": branch_summary["shape"],
            "branch_count": branch_count,
            "alive_count": branch_summary["alive_count"],
        },
        "reduction": reduction_summary,
        "metrics": {
            "branch_count": branch_count,
            "selected_action_count": selected_action_count,
            "success": success,
        },
    }


def write_report(report: dict[str, Any], out_path: str | Path) -> None:
    """Write a demo report as stable JSON."""

    with Path(out_path).open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
