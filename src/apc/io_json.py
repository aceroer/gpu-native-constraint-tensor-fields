"""JSON I/O for native problem specs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .spec import BinaryDomainSpec, LinearCSRSpec, ObjectiveSpec, ProblemSpec


def load_problem_json(path: str | Path) -> ProblemSpec:
    """Load and validate a native problem spec from JSON."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return problem_from_json_dict(data)


def save_problem_json(problem: ProblemSpec, path: str | Path) -> None:
    """Write a problem spec as canonical JSON."""

    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(problem_to_json_dict(problem), handle, indent=2, sort_keys=True)
        handle.write("\n")


def problem_from_json_dict(data: dict[str, Any]) -> ProblemSpec:
    """Validate a JSON dictionary and return typed spec objects."""

    if not isinstance(data, dict):
        raise ValueError("problem spec must be a JSON object")

    domain_data = _object(data, "domain")
    if domain_data.get("type") != "binary":
        raise ValueError("only binary domains are supported in Phase 1")
    domain = BinaryDomainSpec(n_vars=_int(domain_data, "n_vars"))

    objective_data = _object(data, "objective")
    objective = ObjectiveSpec(linear=_float_tuple(objective_data, "linear"))

    constraints_data = _object(data, "constraints")
    linear_data = _object(constraints_data, "linear_csr")
    linear = LinearCSRSpec(
        n_rows=_int(linear_data, "n_rows"),
        row_ptr=_int_tuple(linear_data, "row_ptr"),
        col_idx=_int_tuple(linear_data, "col_idx"),
        coeff=_float_tuple(linear_data, "coeff"),
        rhs=_float_tuple(linear_data, "rhs"),
        sense=_str_tuple(linear_data, "sense"),
        weight=_float_tuple(linear_data, "weight"),
    )

    return ProblemSpec(domain=domain, objective=objective, linear_csr=linear)


def problem_to_json_dict(problem: ProblemSpec) -> dict[str, Any]:
    """Convert typed spec objects into the public JSON shape."""

    return {
        "domain": {
            "type": "binary",
            "n_vars": problem.domain.n_vars,
        },
        "objective": {
            "linear": list(problem.objective.linear),
        },
        "constraints": {
            "linear_csr": {
                "n_rows": problem.linear_csr.n_rows,
                "row_ptr": list(problem.linear_csr.row_ptr),
                "col_idx": list(problem.linear_csr.col_idx),
                "coeff": list(problem.linear_csr.coeff),
                "rhs": list(problem.linear_csr.rhs),
                "sense": list(problem.linear_csr.sense),
                "weight": list(problem.linear_csr.weight),
            }
        },
    }


def _object(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _int_tuple(data: dict[str, Any], key: str) -> tuple[int, ...]:
    values = data.get(key)
    if not isinstance(values, list) or not all(isinstance(value, int) for value in values):
        raise ValueError(f"{key} must be a list of integers")
    return tuple(values)


def _float_tuple(data: dict[str, Any], key: str) -> tuple[float, ...]:
    values = data.get(key)
    if not isinstance(values, list):
        raise ValueError(f"{key} must be a list of numbers")
    converted: list[float] = []
    for value in values:
        if not isinstance(value, int | float):
            raise ValueError(f"{key} must be a list of numbers")
        converted.append(float(value))
    return tuple(converted)


def _str_tuple(data: dict[str, Any], key: str) -> tuple[str, ...]:
    values = data.get(key)
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError(f"{key} must be a list of strings")
    return tuple(values)

