"""Weighted MaxSAT reading and CPU reference operators."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..ctir import (
    CTIRProblem,
    ClauseCSR,
    LedgerSpec,
    MoveBatch,
    ObjectiveLinear,
    ProjectionSpec,
    StateBatch,
    VarDomain,
)


@dataclass(frozen=True)
class MaxSATClause:
    """One weighted clause using one-based DIMACS-style literals."""

    literals: tuple[int, ...]
    weight: float

    def __post_init__(self) -> None:
        if len(self.literals) == 0:
            raise ValueError("MaxSATClause.literals must not be empty")
        if 0 in self.literals:
            raise ValueError("MaxSAT literals must be nonzero")
        if self.weight < 0.0:
            raise ValueError("MaxSATClause.weight must be nonnegative")


@dataclass(frozen=True)
class MaxSATSpec:
    """Tiny weighted MaxSAT input spec."""

    n_vars: int
    clauses: tuple[MaxSATClause, ...]

    def __post_init__(self) -> None:
        if self.n_vars <= 0:
            raise ValueError("MaxSATSpec.n_vars must be positive")
        if len(self.clauses) == 0:
            raise ValueError("MaxSATSpec.clauses must not be empty")
        bad = [lit for clause in self.clauses for lit in clause.literals if abs(lit) > self.n_vars]
        if bad:
            raise ValueError(f"MaxSAT literal variable out of range: {bad}")


@dataclass(frozen=True)
class MaxSATRepairResult:
    """Result from the small CPU bit-flip MaxSAT repair loop."""

    best_state: tuple[int, ...]
    best_penalty: float
    unsatisfied: tuple[int, ...]
    final_states: StateBatch


def load_maxsat_json(path: str | Path) -> MaxSATSpec:
    """Load a weighted MaxSAT JSON spec."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return maxsat_from_json_dict(data)


def maxsat_from_json_dict(data: dict[str, Any]) -> MaxSATSpec:
    """Validate a weighted MaxSAT JSON dictionary."""

    if not isinstance(data, dict):
        raise ValueError("MaxSAT spec must be a JSON object")
    if data.get("problem_type") != "weighted_maxsat":
        raise ValueError("problem_type must be weighted_maxsat")
    domain = data.get("domain")
    if not isinstance(domain, dict) or domain.get("type") != "binary":
        raise ValueError("MaxSAT domain must be binary")
    n_vars = domain.get("n_vars")
    if not isinstance(n_vars, int):
        raise ValueError("domain.n_vars must be an integer")
    raw_clauses = data.get("clauses")
    if not isinstance(raw_clauses, list):
        raise ValueError("clauses must be a list")

    clauses: list[MaxSATClause] = []
    for raw in raw_clauses:
        if not isinstance(raw, dict):
            raise ValueError("each clause must be an object")
        literals = raw.get("lits")
        weight = raw.get("weight")
        if not isinstance(literals, list) or not all(isinstance(lit, int) for lit in literals):
            raise ValueError("clause.lits must be a list of integers")
        if not isinstance(weight, int | float):
            raise ValueError("clause.weight must be a number")
        clauses.append(MaxSATClause(literals=tuple(literals), weight=float(weight)))

    return MaxSATSpec(n_vars=n_vars, clauses=tuple(clauses))


def lower_maxsat_to_ctir(
    spec: MaxSATSpec,
    *,
    batch_size: int = 4,
    moves_per_state: int | None = None,
) -> CTIRProblem:
    """Lower weighted MaxSAT into CTIR ClauseCSR."""

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    clause_ptr = [0]
    lit_var: list[int] = []
    lit_sign: list[int] = []
    weight: list[float] = []
    for clause in spec.clauses:
        for lit in clause.literals:
            lit_var.append(abs(lit) - 1)
            lit_sign.append(1 if lit > 0 else -1)
        clause_ptr.append(len(lit_var))
        weight.append(clause.weight)

    return CTIRProblem(
        domain=VarDomain(n_vars=spec.n_vars, var_type=tuple("binary" for _ in range(spec.n_vars))),
        objective=ObjectiveLinear(coeff=tuple(0.0 for _ in range(spec.n_vars))),
        linear_csr=None,
        clause_csr=ClauseCSR(
            n_clauses=len(spec.clauses),
            clause_ptr=tuple(clause_ptr),
            lit_var=tuple(lit_var),
            lit_sign=tuple(lit_sign),
            weight=tuple(weight),
        ),
        qubo_coo=None,
        projection=ProjectionSpec(rules=("binary",)),
        moves=MoveBatch(
            batch_size=batch_size,
            moves_per_state=moves_per_state if moves_per_state is not None else spec.n_vars,
            move_type="bit_flip",
            move_dim=1,
        ),
        ledger=LedgerSpec(fields=("objective", "penalty", "feasible_count", "active_violation_count")),
    )


def eval_unsatisfied_clauses(
    clause: ClauseCSR,
    states: StateBatch,
) -> tuple[tuple[int, ...], ...]:
    """Evaluate unsatisfied clause indicators for each state."""

    rows: list[tuple[int, ...]] = []
    for state in states.x:
        if any(value not in (0, 1) for value in state):
            raise ValueError("MaxSAT CPU evaluation supports binary states only")
        unsatisfied: list[int] = []
        for clause_index in range(clause.n_clauses):
            start = clause.clause_ptr[clause_index]
            end = clause.clause_ptr[clause_index + 1]
            satisfied = False
            for offset in range(start, end):
                value = state[clause.lit_var[offset]]
                sign = clause.lit_sign[offset]
                if (sign == 1 and value == 1) or (sign == -1 and value == 0):
                    satisfied = True
                    break
            unsatisfied.append(0 if satisfied else 1)
        rows.append(tuple(unsatisfied))
    return tuple(rows)


def maxsat_penalty(
    clause: ClauseCSR,
    unsatisfied: tuple[tuple[int, ...], ...],
) -> tuple[float, ...]:
    """Reduce weighted unsatisfied indicators into penalties."""

    penalties: list[float] = []
    for row in unsatisfied:
        if len(row) != clause.n_clauses:
            raise ValueError("unsatisfied row length must equal n_clauses")
        penalties.append(sum(flag * weight for flag, weight in zip(row, clause.weight)))
    return tuple(penalties)


def run_maxsat_bitflip_repair(
    problem: CTIRProblem,
    *,
    max_iters: int = 8,
    seed: int = 0,
    initial_states: StateBatch | None = None,
) -> MaxSATRepairResult:
    """Run a small deterministic CPU bit-flip MaxSAT repair loop."""

    if problem.clause_csr is None:
        raise ValueError("MaxSAT repair requires clause_csr")
    if max_iters < 0:
        raise ValueError("max_iters must be nonnegative")
    states = initial_states if initial_states is not None else _initial_states(problem, seed)
    best_state, best_penalty, best_unsatisfied = _best_clause_state(problem.clause_csr, states)

    for _ in range(max_iters):
        next_states = []
        for state in states.x:
            next_states.append(_best_single_flip(problem.clause_csr, state))
        states = StateBatch(tuple(next_states))
        candidate_state, candidate_penalty, candidate_unsatisfied = _best_clause_state(problem.clause_csr, states)
        if (candidate_penalty, candidate_state) < (best_penalty, best_state):
            best_state = candidate_state
            best_penalty = candidate_penalty
            best_unsatisfied = candidate_unsatisfied

    return MaxSATRepairResult(
        best_state=best_state,
        best_penalty=best_penalty,
        unsatisfied=best_unsatisfied,
        final_states=states,
    )


def _best_clause_state(clause: ClauseCSR, states: StateBatch) -> tuple[tuple[int, ...], float, tuple[int, ...]]:
    unsatisfied = eval_unsatisfied_clauses(clause, states)
    penalties = maxsat_penalty(clause, unsatisfied)
    index = min(range(states.batch_size), key=lambda i: (penalties[i], states.x[i]))
    return states.x[index], penalties[index], unsatisfied[index]


def _best_single_flip(clause: ClauseCSR, state: tuple[int, ...]) -> tuple[int, ...]:
    candidates = [state]
    for var in range(len(state)):
        updated = list(state)
        updated[var] = 1 - updated[var]
        candidates.append(tuple(updated))
    batch = StateBatch(tuple(candidates))
    best, _, _ = _best_clause_state(clause, batch)
    return best


def _initial_states(problem: CTIRProblem, seed: int) -> StateBatch:
    rng = random.Random(seed)
    states = [tuple(0 for _ in range(problem.domain.n_vars))]
    for _ in range(problem.moves.batch_size - 1):
        states.append(tuple(rng.randint(0, 1) for _ in range(problem.domain.n_vars)))
    return StateBatch(tuple(states))
