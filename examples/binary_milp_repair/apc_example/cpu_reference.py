"""CPU reference operators for binary MILP repair."""

from __future__ import annotations

from .ctir import BinaryDomain, LinearCSR, StateBatch


def eval_linear_response(batch: StateBatch, linear: LinearCSR) -> list[list[float]]:
    """Evaluate raw linear row response for every candidate."""

    responses: list[list[float]] = []
    for x in batch.x:
        row_values: list[float] = []
        for row in range(linear.n_rows):
            start = linear.row_ptr[row]
            end = linear.row_ptr[row + 1]
            value = 0.0
            for offset in range(start, end):
                value += linear.coeff[offset] * x[linear.col_idx[offset]]
            row_values.append(value - linear.rhs[row])
        responses.append(row_values)
    return responses


def positive_violation(response: list[list[float]], linear: LinearCSR) -> list[list[float]]:
    """Rectify raw response into nonnegative violation."""

    violations: list[list[float]] = []
    for candidate_response in response:
        candidate_violation: list[float] = []
        for row, value in enumerate(candidate_response):
            sense = linear.sense[row]
            if sense == "<=":
                violation = max(value, 0.0)
            elif sense == ">=":
                violation = max(-value, 0.0)
            else:
                violation = abs(value)
            candidate_violation.append(violation)
        violations.append(candidate_violation)
    return violations


def weighted_penalty(violations: list[list[float]], linear: LinearCSR) -> list[float]:
    """Reduce row violations into one weighted penalty per candidate."""

    penalties: list[float] = []
    for candidate_violation in violations:
        penalty = 0.0
        for row, violation in enumerate(candidate_violation):
            penalty += linear.weight[row] * violation
        penalties.append(penalty)
    return penalties


def objective(batch: StateBatch, cost: tuple[float, ...]) -> list[float]:
    """Evaluate c^T x."""

    values: list[float] = []
    for x in batch.x:
        values.append(sum(c * xi for c, xi in zip(cost, x, strict=True)))
    return values


def energy(
    batch: StateBatch,
    linear: LinearCSR,
    cost: tuple[float, ...],
    lambda_penalty: float,
    objective_weight: float,
) -> tuple[list[float], list[float], list[list[float]]]:
    """Compute objective + penalty energy and return ledger pieces."""

    response = eval_linear_response(batch, linear)
    violations = positive_violation(response, linear)
    penalties = weighted_penalty(violations, linear)
    objectives = objective(batch, cost)
    values = [
        objective_weight * obj + lambda_penalty * penalty
        for obj, penalty in zip(objectives, penalties, strict=True)
    ]
    return values, penalties, violations


def project_binary(batch: StateBatch, domain: BinaryDomain) -> StateBatch:
    """Projection closure for binary states."""

    projected: list[tuple[int, ...]] = []
    for x in batch.x:
        if len(x) != domain.n_vars:
            raise ValueError("state width does not match domain")
        projected.append(tuple(1 if value else 0 for value in x))
    return StateBatch(tuple(projected))


def flip_one(batch: StateBatch, candidate: int, variable: int) -> StateBatch:
    """Return a copy of the batch with one bit flipped."""

    updated = [list(x) for x in batch.x]
    updated[candidate][variable] = 1 - updated[candidate][variable]
    return StateBatch(tuple(tuple(x) for x in updated))

