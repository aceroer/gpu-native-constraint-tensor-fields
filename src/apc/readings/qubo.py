"""QUBO reading and CTIR lowering route."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..ctir import (
    CTIRProblem,
    LedgerSpec,
    MoveBatch,
    ObjectiveLinear,
    ProjectionSpec,
    QUBOCOO,
    VarDomain,
)
from ..runtime_status import FAILED, PLANNED


@dataclass(frozen=True)
class QUBOTerm:
    """One QUBO term using zero-based variable indices."""

    i: int
    j: int
    weight: float

    def __post_init__(self) -> None:
        if self.i < 0 or self.j < 0:
            raise ValueError("QUBOTerm indices must be nonnegative")


@dataclass(frozen=True)
class QUBOSpec:
    """Tiny public QUBO input spec."""

    n_vars: int
    linear: tuple[float, ...]
    quadratic: tuple[QUBOTerm, ...]

    def __post_init__(self) -> None:
        if self.n_vars <= 0:
            raise ValueError("QUBOSpec.n_vars must be positive")
        if len(self.linear) != self.n_vars:
            raise ValueError("QUBOSpec.linear length must equal n_vars")
        if len(self.quadratic) == 0:
            raise ValueError("QUBOSpec.quadratic must not be empty")
        bad = [
            (term.i, term.j)
            for term in self.quadratic
            if term.i >= self.n_vars or term.j >= self.n_vars
        ]
        if bad:
            raise ValueError(f"QUBO term indices out of range: {bad}")


def load_qubo_json(path: str | Path) -> QUBOSpec:
    """Load a QUBO JSON spec."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return qubo_from_json_dict(data)


def qubo_from_json_dict(data: dict[str, Any]) -> QUBOSpec:
    """Validate a QUBO JSON dictionary."""

    if not isinstance(data, dict):
        raise ValueError("QUBO spec must be a JSON object")
    if data.get("problem_type") != "qubo":
        raise ValueError("problem_type must be qubo")
    unsupported = [key for key in data if key not in {"problem_type", "domain", "objective"}]
    if unsupported:
        raise ValueError(f"unsupported QUBO fields: {unsupported}")
    domain = data.get("domain")
    if not isinstance(domain, dict) or domain.get("type") != "binary":
        raise ValueError("QUBO domain must be binary")
    n_vars = domain.get("n_vars")
    if not isinstance(n_vars, int):
        raise ValueError("domain.n_vars must be an integer")
    objective = data.get("objective")
    if not isinstance(objective, dict):
        raise ValueError("objective must be an object")
    unsupported_objective = [key for key in objective if key not in {"linear", "quadratic"}]
    if unsupported_objective:
        raise ValueError(f"unsupported QUBO objective fields: {unsupported_objective}")
    linear = _number_list(objective.get("linear"), "objective.linear")
    quadratic = objective.get("quadratic")
    if not isinstance(quadratic, list):
        raise ValueError("objective.quadratic must be a list")

    terms: list[QUBOTerm] = []
    for raw in quadratic:
        if not isinstance(raw, dict):
            raise ValueError("each QUBO quadratic term must be an object")
        unsupported_term = [key for key in raw if key not in {"i", "j", "weight"}]
        if unsupported_term:
            raise ValueError(f"unsupported QUBO term fields: {unsupported_term}")
        i = raw.get("i")
        j = raw.get("j")
        weight = raw.get("weight")
        if not isinstance(i, int) or not isinstance(j, int):
            raise ValueError("QUBO term i and j must be integers")
        if not isinstance(weight, int | float):
            raise ValueError("QUBO term weight must be a number")
        terms.append(QUBOTerm(i=i, j=j, weight=float(weight)))

    return QUBOSpec(n_vars=n_vars, linear=tuple(linear), quadratic=tuple(terms))


def lower_qubo_to_ctir(
    spec: QUBOSpec,
    *,
    batch_size: int = 4,
    moves_per_state: int | None = None,
) -> CTIRProblem:
    """Lower QUBO into CTIR objective and COO energy metadata."""

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    return CTIRProblem(
        domain=VarDomain(n_vars=spec.n_vars, var_type=tuple("binary" for _ in range(spec.n_vars))),
        objective=ObjectiveLinear(coeff=spec.linear),
        linear_csr=None,
        clause_csr=None,
        qubo_coo=QUBOCOO(
            n_vars=spec.n_vars,
            i=tuple(term.i for term in spec.quadratic),
            j=tuple(term.j for term in spec.quadratic),
            q=tuple(term.weight for term in spec.quadratic),
        ),
        projection=ProjectionSpec(rules=("binary",)),
        moves=MoveBatch(
            batch_size=batch_size,
            moves_per_state=moves_per_state if moves_per_state is not None else spec.n_vars,
            move_type="bit_flip",
            move_dim=1,
        ),
        ledger=LedgerSpec(fields=("objective", "penalty")),
    )


def describe_qubo_lowering_from_json(
    path: str | Path,
    *,
    batch_size: int = 4,
) -> dict[str, Any]:
    """Return a JSON-ready QUBO lowering report without executing a runtime."""

    try:
        spec = load_qubo_json(path)
        problem = lower_qubo_to_ctir(spec, batch_size=batch_size)
    except Exception as exc:
        return {
            "schema": "apc.qubo_lowering.v1",
            "status": FAILED,
            "reason": str(exc),
            "source_path": str(path),
            "problem_family": "qubo",
            "execution_status": PLANNED,
            "notes": [
                "Unsupported QUBO features fail as structured lowering status.",
                "Use the QUBO CPU reference execution route to run this problem family.",
            ],
        }

    qubo = problem.qubo_coo
    return {
        "schema": "apc.qubo_lowering.v1",
        "status": "implemented",
        "source_path": str(path),
        "problem_family": "qubo",
        "execution_status": PLANNED,
        "ctir": {
            "n_vars": problem.domain.n_vars,
            "linear_terms": list(problem.objective.coeff),
            "quadratic_terms": [
                {
                    "i": i,
                    "j": j,
                    "weight": q,
                }
                for i, j, q in zip(qubo.i, qubo.j, qubo.q, strict=True)
            ]
            if qubo is not None
            else [],
            "qubo_nnz": len(qubo.q) if qubo is not None else 0,
        },
        "config": {
            "batch_size": batch_size,
        },
        "notes": [
            "QUBO COO entries are CTIR energy metadata.",
            "Linear and quadratic terms are recorded explicitly.",
            "This lowering report does not execute the CPU reference route.",
        ],
    }


def _number_list(value: Any, name: str) -> list[float]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    converted: list[float] = []
    for item in value:
        if not isinstance(item, int | float):
            raise ValueError(f"{name} must be a list of numbers")
        converted.append(float(item))
    return converted
