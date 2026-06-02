"""Deterministic CPU repair runtime."""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

from .ctir import CTIRProblem, StateBatch
from .io_json import load_problem_json
from .ledger import LedgerRow
from .lowering import lower_problem_to_ctir
from .operators_cpu import (
    apply_moves,
    apply_projection,
    eval_constraints,
    generate_moves,
    objective_values,
    record_metrics,
    rectify_violations,
    reduce_best,
    reduce_penalty,
    score_moves,
    select_moves,
)


@dataclass(frozen=True)
class RuntimeConfig:
    """CPU runtime controls."""

    max_iters: int = 8
    batch_size: int = 4
    seed: int = 0
    penalty_weight: float = 10.0

    def __post_init__(self) -> None:
        if self.max_iters < 0:
            raise ValueError("max_iters must be nonnegative")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.penalty_weight <= 0.0:
            raise ValueError("penalty_weight must be positive")


@dataclass(frozen=True)
class RuntimeResult:
    """CPU runtime output."""

    best_state: tuple[int, ...]
    best_objective: float
    best_penalty: float
    ledger: tuple[LedgerRow, ...]
    final_states: StateBatch


def run_repair(
    problem: CTIRProblem,
    *,
    config: RuntimeConfig | None = None,
    initial_states: StateBatch | None = None,
) -> RuntimeResult:
    """Run a deterministic repair loop over CTIR."""

    cfg = config or RuntimeConfig(batch_size=problem.moves.batch_size)
    states = initial_states if initial_states is not None else _initial_states(problem, cfg)
    states = apply_projection(problem, states)

    ledger: list[LedgerRow] = []
    best_state: tuple[int, ...] | None = None
    best_objective = 0.0
    best_penalty = 0.0

    for iteration in range(cfg.max_iters + 1):
        responses = eval_constraints(problem, states)
        violations = rectify_violations(problem, responses)
        penalties = reduce_penalty(problem, violations)
        objectives = objective_values(problem, states)
        row = record_metrics(
            problem,
            iteration,
            states,
            objectives,
            penalties,
            violations,
            penalty_weight=cfg.penalty_weight,
        )
        ledger.append(row)

        candidate_state, candidate_objective, candidate_penalty = reduce_best(
            problem,
            states,
            objectives,
            penalties,
            penalty_weight=cfg.penalty_weight,
        )
        if best_state is None or _is_better(
            candidate_objective,
            candidate_penalty,
            best_objective,
            best_penalty,
            cfg.penalty_weight,
        ):
            best_state = candidate_state
            best_objective = candidate_objective
            best_penalty = candidate_penalty

        if iteration == cfg.max_iters:
            break

        moves = generate_moves(problem, states)
        scored = score_moves(problem, states, moves, penalty_weight=cfg.penalty_weight)
        selected = select_moves(scored)
        next_states = apply_projection(problem, apply_moves(states, selected))
        if next_states == states:
            continue
        states = next_states

    if best_state is None:
        raise RuntimeError("runtime did not evaluate any states")
    return RuntimeResult(
        best_state=best_state,
        best_objective=best_objective,
        best_penalty=best_penalty,
        ledger=tuple(ledger),
        final_states=states,
    )


def run_repair_from_json(
    path: str | Path,
    *,
    config: RuntimeConfig | None = None,
    initial_states: StateBatch | None = None,
) -> RuntimeResult:
    """Load a JSON spec, lower it to CTIR, and run the CPU repair loop."""

    cfg = config or RuntimeConfig()
    spec = load_problem_json(path)
    problem = lower_problem_to_ctir(spec, batch_size=cfg.batch_size)
    return run_repair(problem, config=cfg, initial_states=initial_states)


def _initial_states(problem: CTIRProblem, config: RuntimeConfig) -> StateBatch:
    rng = random.Random(config.seed)
    states = []
    for row in range(config.batch_size):
        if row == 0:
            states.append(tuple(0 for _ in range(problem.domain.n_vars)))
        else:
            states.append(tuple(rng.randint(0, 1) for _ in range(problem.domain.n_vars)))
    return StateBatch(tuple(states))


def _is_better(
    objective: float,
    penalty: float,
    best_objective: float,
    best_penalty: float,
    penalty_weight: float,
) -> bool:
    rank = (0 if penalty == 0.0 else 1, objective + penalty_weight * penalty, penalty, objective)
    best_rank = (
        0 if best_penalty == 0.0 else 1,
        best_objective + penalty_weight * best_penalty,
        best_penalty,
        best_objective,
    )
    return rank < best_rank
