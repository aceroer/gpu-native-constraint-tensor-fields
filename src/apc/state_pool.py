"""Native state pool objects for batched repair runtimes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ctir import CTIRProblem, StateBatch


@dataclass(frozen=True)
class StatePool:
    """A candidate-major state pool with runtime annotations."""

    states: StateBatch
    scores: tuple[float, ...]
    uncertainty: tuple[float, ...]
    alive_mask: tuple[bool, ...]
    metadata: tuple[dict[str, Any], ...]

    def __post_init__(self) -> None:
        batch_size = self.states.batch_size
        if batch_size <= 0:
            raise ValueError("StatePool.states must not be empty")
        if self.states.n_vars <= 0:
            raise ValueError("StatePool states must include variables")
        if len(self.scores) != batch_size:
            raise ValueError("StatePool.scores length must equal batch size")
        if len(self.uncertainty) != batch_size:
            raise ValueError("StatePool.uncertainty length must equal batch size")
        if len(self.alive_mask) != batch_size:
            raise ValueError("StatePool.alive_mask length must equal batch size")
        if len(self.metadata) != batch_size:
            raise ValueError("StatePool.metadata length must equal batch size")
        if any(len(row) != self.states.n_vars for row in self.states.x):
            raise ValueError("all StatePool rows must have the same width")
        if any(value < 0.0 for value in self.uncertainty):
            raise ValueError("StatePool.uncertainty values must be nonnegative")

    @property
    def batch_size(self) -> int:
        return self.states.batch_size

    @property
    def n_vars(self) -> int:
        return self.states.n_vars

    @property
    def alive_count(self) -> int:
        return sum(1 for alive in self.alive_mask if alive)


def initialize_state_pool(problem: CTIRProblem, *, seed_zero: bool = True) -> StatePool:
    """Initialize a deterministic StatePool from CTIR batch metadata."""

    rows: list[tuple[int, ...]] = []
    for row in range(problem.moves.batch_size):
        if seed_zero and row == 0:
            rows.append(tuple(0 for _ in range(problem.domain.n_vars)))
        else:
            rows.append(tuple((row + col) % 2 for col in range(problem.domain.n_vars)))
    return StatePool(
        states=StateBatch(tuple(rows)),
        scores=tuple(0.0 for _ in rows),
        uncertainty=tuple(1.0 for _ in rows),
        alive_mask=tuple(True for _ in rows),
        metadata=tuple({"origin": "ctir_init", "row": row} for row in range(len(rows))),
    )


def state_pool_with_scores(pool: StatePool, scores: tuple[float, ...]) -> StatePool:
    """Return a StatePool with updated scores."""

    return StatePool(
        states=pool.states,
        scores=scores,
        uncertainty=pool.uncertainty,
        alive_mask=pool.alive_mask,
        metadata=pool.metadata,
    )


def mask_state_pool(pool: StatePool, alive_mask: tuple[bool, ...]) -> StatePool:
    """Return a StatePool with an updated alive mask."""

    return StatePool(
        states=pool.states,
        scores=pool.scores,
        uncertainty=pool.uncertainty,
        alive_mask=alive_mask,
        metadata=pool.metadata,
    )


def state_pool_summary(pool: StatePool) -> dict[str, Any]:
    """Return a compact JSON-ready state pool summary."""

    return {
        "batch_size": pool.batch_size,
        "n_vars": pool.n_vars,
        "alive_count": pool.alive_count,
        "scores": list(pool.scores),
        "uncertainty": list(pool.uncertainty),
        "alive_mask": list(pool.alive_mask),
        "metadata": [dict(row) for row in pool.metadata],
    }
