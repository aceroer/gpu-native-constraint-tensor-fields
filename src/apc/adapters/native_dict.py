"""Adapter from public native dictionaries into APC execution objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..ctir import CTIRProblem
from ..io_json import problem_from_json_dict
from ..interface_projection import interface_projection_to_dict, project_adapter_summary
from ..layout import layout_summary, plan_layout
from ..lowering import lower_problem_to_ctir
from ..operator_registry import default_operator_registry, registry_summary
from ..spec import ProblemSpec


UNSUPPORTED_FEATURE_KEYS = (
    "branching",
    "callbacks",
    "cutting_planes",
    "lazy_constraints",
    "presolve",
    "solver",
)


@dataclass(frozen=True)
class AdapterResult:
    """Result of lowering an adapter input through the native pipeline."""

    source: str
    problem: ProblemSpec
    ctir: CTIRProblem
    layout: dict[str, Any]
    registry: dict[str, Any]


def lower_native_binary_milp_dict(data: dict[str, Any], *, batch_size: int = 4) -> AdapterResult:
    """Lower a native binary MILP dictionary through spec, CTIR, layout, and registry."""

    unsupported = tuple(key for key in UNSUPPORTED_FEATURE_KEYS if key in data)
    if unsupported:
        joined = ", ".join(unsupported)
        raise ValueError(f"unsupported adapter features: {joined}")

    problem = problem_from_json_dict(data)
    ctir = lower_problem_to_ctir(problem, batch_size=batch_size)
    layout = layout_summary(plan_layout(ctir))
    registry = registry_summary(default_operator_registry())
    return AdapterResult(
        source="native_binary_milp_dict",
        problem=problem,
        ctir=ctir,
        layout=layout,
        registry=registry,
    )


def adapter_result_to_dict(result: AdapterResult) -> dict[str, Any]:
    """Return a compact JSON-ready adapter summary."""

    payload = {
        "source": result.source,
        "n_vars": result.problem.domain.n_vars,
        "n_constraints": result.problem.linear_csr.n_rows,
        "batch_size": result.ctir.moves.batch_size,
        "layout_views": [view["name"] for view in result.layout["views"]],
        "operators": [operator["name"] for operator in result.registry["operators"]],
    }
    return interface_projection_to_dict(project_adapter_summary(payload))
