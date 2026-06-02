"""Deterministic reduction gates for branch tensors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .branch_tensor import BranchRoute, BranchTensor
from .ctir import CTIRProblem, StateBatch
from .operators_cpu import eval_constraints, objective_values, rectify_violations, reduce_penalty
from .state_pool import StatePool


@dataclass(frozen=True)
class ReductionConfig:
    """Controls for deterministic route reduction."""

    top_k: int = 1
    penalty_weight: float = 10.0
    diversity_weight: float = 0.0

    def __post_init__(self) -> None:
        if self.top_k <= 0:
            raise ValueError("ReductionConfig.top_k must be positive")
        if self.penalty_weight <= 0.0:
            raise ValueError("ReductionConfig.penalty_weight must be positive")
        if self.diversity_weight < 0.0:
            raise ValueError("ReductionConfig.diversity_weight must be nonnegative")


@dataclass(frozen=True)
class RouteDecision:
    """One scored route decision."""

    route: BranchRoute
    energy: float
    objective: float
    penalty: float
    diversity_penalty: float
    selected: bool
    rank: int | None = None

    @property
    def adjusted_energy(self) -> float:
        return self.energy + self.diversity_penalty


@dataclass(frozen=True)
class ReductionGateResult:
    """Output of reducing a branch tensor into selected actions."""

    selected: tuple[RouteDecision, ...]
    candidates: tuple[RouteDecision, ...]
    config: ReductionConfig


def reduce_branch_tensor(
    problem: CTIRProblem,
    pool: StatePool,
    tensor: BranchTensor,
    *,
    config: ReductionConfig | None = None,
) -> ReductionGateResult:
    """Select top-k alive routes with deterministic diversity accounting."""

    cfg = config or ReductionConfig()
    candidates = _score_alive_routes(problem, pool, tensor, cfg)
    selected: list[RouteDecision] = []
    remaining = list(candidates)
    canonical_counts: dict[tuple[str, tuple[int, ...]], int] = {}

    while remaining and len(selected) < cfg.top_k:
        ranked: list[tuple[tuple[float, float, float, int, int], int, RouteDecision]] = []
        for index, candidate in enumerate(remaining):
            diversity_penalty = cfg.diversity_weight * canonical_counts.get(
                candidate.route.canonical_key,
                0,
            )
            rank_key = (
                candidate.energy + diversity_penalty,
                candidate.penalty,
                candidate.objective,
                candidate.route.route_index,
                candidate.route.state_index,
            )
            ranked.append((rank_key, index, candidate))
        _, index, winner = min(ranked)
        diversity_penalty = cfg.diversity_weight * canonical_counts.get(
            winner.route.canonical_key,
            0,
        )
        selected_decision = RouteDecision(
            route=winner.route,
            energy=winner.energy,
            objective=winner.objective,
            penalty=winner.penalty,
            diversity_penalty=diversity_penalty,
            selected=True,
            rank=len(selected),
        )
        selected.append(selected_decision)
        canonical_counts[winner.route.canonical_key] = (
            canonical_counts.get(winner.route.canonical_key, 0) + 1
        )
        remaining.pop(index)

    selected_keys = {(decision.route.state_index, decision.route.route_index) for decision in selected}
    unselected = tuple(
        RouteDecision(
            route=candidate.route,
            energy=candidate.energy,
            objective=candidate.objective,
            penalty=candidate.penalty,
            diversity_penalty=0.0,
            selected=False,
        )
        for candidate in candidates
        if (candidate.route.state_index, candidate.route.route_index) not in selected_keys
    )
    return ReductionGateResult(
        selected=tuple(selected),
        candidates=tuple(selected) + unselected,
        config=cfg,
    )


def reduction_gate_summary(result: ReductionGateResult) -> dict[str, Any]:
    """Return a compact JSON-ready reduction summary."""

    return {
        "top_k": result.config.top_k,
        "selected_count": len(result.selected),
        "penalty_weight": result.config.penalty_weight,
        "diversity_weight": result.config.diversity_weight,
        "selected": [_decision_to_dict(decision) for decision in result.selected],
    }


def _score_alive_routes(
    problem: CTIRProblem,
    pool: StatePool,
    tensor: BranchTensor,
    config: ReductionConfig,
) -> tuple[RouteDecision, ...]:
    if tensor.batch_size != pool.batch_size:
        raise ValueError("BranchTensor batch size must match StatePool")
    decisions: list[RouteDecision] = []
    for state_index, row in enumerate(tensor.routes):
        for route_index, route in enumerate(row):
            if not tensor.alive_mask[state_index][route_index]:
                continue
            candidate_state = _apply_route(pool.states.x[route.state_index], route)
            candidate_batch = StateBatch((candidate_state,))
            objective = objective_values(problem, candidate_batch)[0]
            penalty = reduce_penalty(
                problem,
                rectify_violations(problem, eval_constraints(problem, candidate_batch)),
            )[0]
            energy = objective + config.penalty_weight * penalty
            decisions.append(
                RouteDecision(
                    route=route,
                    energy=energy,
                    objective=objective,
                    penalty=penalty,
                    diversity_penalty=0.0,
                    selected=False,
                )
            )
    return tuple(decisions)


def _apply_route(state: tuple[int, ...], route: BranchRoute) -> tuple[int, ...]:
    if route.move_type != "bit_flip":
        raise ValueError(f"unsupported branch route type: {route.move_type}")
    if len(route.payload) != 1:
        raise ValueError("bit_flip route payload must contain one variable index")
    var_index = route.payload[0]
    if var_index < 0 or var_index >= len(state):
        raise ValueError("bit_flip route variable index out of range")
    updated = list(state)
    updated[var_index] = 1 - updated[var_index]
    return tuple(updated)


def _decision_to_dict(decision: RouteDecision) -> dict[str, Any]:
    return {
        "rank": decision.rank,
        "state_index": decision.route.state_index,
        "route_index": decision.route.route_index,
        "move_type": decision.route.move_type,
        "payload": list(decision.route.payload),
        "energy": decision.energy,
        "objective": decision.objective,
        "penalty": decision.penalty,
        "diversity_penalty": decision.diversity_penalty,
        "adjusted_energy": decision.adjusted_energy,
    }
