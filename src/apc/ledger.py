"""Validation ledger records emitted by runtimes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LedgerRow:
    """One runtime validation row."""

    iteration: int
    objective: float
    penalty: float
    feasible_count: int
    active_violation_count: int


def ledger_to_dicts(rows: tuple[LedgerRow, ...]) -> list[dict[str, float | int]]:
    """Convert ledger rows into JSON-friendly dictionaries."""

    return [
        {
            "iteration": row.iteration,
            "objective": row.objective,
            "penalty": row.penalty,
            "feasible_count": row.feasible_count,
            "active_violation_count": row.active_violation_count,
        }
        for row in rows
    ]
