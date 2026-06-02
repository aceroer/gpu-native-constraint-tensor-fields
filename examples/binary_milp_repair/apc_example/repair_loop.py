"""A tiny binary MILP repair loop.

The code is intentionally simple. It is not a competitive solver; it is a
walking example of the method:

response -> violation -> feedback move scoring -> projection -> ledger.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cpu_reference import energy, flip_one, project_binary
from .ctir import BinaryDomain, LinearCSR, RepairConfig, StateBatch


@dataclass(frozen=True)
class RepairResult:
    best_state: tuple[int, ...] | None
    best_objective: float | None
    best_penalty: float | None
    final_batch: StateBatch
    ledger: tuple[dict[str, float | int], ...]


def repair_binary_milp(
    domain: BinaryDomain,
    linear: LinearCSR,
    cost: tuple[float, ...],
    initial_batch: StateBatch,
    config: RepairConfig,
) -> RepairResult:
    """Run a greedy batched bit-flip repair loop."""

    batch = project_binary(initial_batch, domain)
    best_state: tuple[int, ...] | None = None
    best_objective: float | None = None
    best_penalty: float | None = None
    ledger: list[dict[str, float | int]] = []

    for iteration in range(config.max_iters):
        energies, penalties, violations = energy(
            batch,
            linear,
            cost,
            config.lambda_penalty,
            config.objective_weight,
        )

        objectives = [
            (e - config.lambda_penalty * p) / config.objective_weight
            for e, p in zip(energies, penalties, strict=True)
        ]
        feasible_count = sum(1 for penalty in penalties if penalty == 0.0)
        for idx, penalty in enumerate(penalties):
            if penalty == 0.0 and (
                best_objective is None or objectives[idx] < best_objective
            ):
                best_state = batch.x[idx]
                best_objective = objectives[idx]
                best_penalty = penalty

        ledger.append(
            {
                "iter": iteration,
                "best_energy": min(energies),
                "best_penalty": min(penalties),
                "feasible_count": feasible_count,
                "active_violation_count": sum(
                    1 for row in violations for value in row if value > 0.0
                ),
            }
        )
        if feasible_count == batch.batch_size:
            break

        batch = _greedy_bitflip_step(domain, linear, cost, batch, config)

    return RepairResult(
        best_state=best_state,
        best_objective=best_objective,
        best_penalty=best_penalty,
        final_batch=batch,
        ledger=tuple(ledger),
    )


def _greedy_bitflip_step(
    domain: BinaryDomain,
    linear: LinearCSR,
    cost: tuple[float, ...],
    batch: StateBatch,
    config: RepairConfig,
) -> StateBatch:
    """Select the best one-bit feedback move per candidate."""

    current_energy, _, _ = energy(
        batch, linear, cost, config.lambda_penalty, config.objective_weight
    )
    next_states: list[tuple[int, ...]] = []

    for candidate in range(batch.batch_size):
        best_candidate_energy = current_energy[candidate]
        best_candidate_state = batch.x[candidate]

        for variable in range(domain.n_vars):
            flipped_batch = flip_one(batch, candidate, variable)
            flipped_energy, _, _ = energy(
                flipped_batch,
                linear,
                cost,
                config.lambda_penalty,
                config.objective_weight,
            )
            if flipped_energy[candidate] < best_candidate_energy:
                best_candidate_energy = flipped_energy[candidate]
                best_candidate_state = flipped_batch.x[candidate]

        next_states.append(best_candidate_state)

    return project_binary(StateBatch(tuple(next_states)), domain)

