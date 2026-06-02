"""CPU implementations of the public operator boundaries."""

from __future__ import annotations

from dataclasses import dataclass

from .ctir import CTIRProblem, StateBatch
from .ledger import LedgerRow


@dataclass(frozen=True)
class Move:
    """A single bit-flip move for one candidate state."""

    state_index: int
    var_index: int


@dataclass(frozen=True)
class ScoredMove:
    """Move score computed against the current candidate energy."""

    move: Move
    energy: float
    objective: float
    penalty: float
    improves: bool


def eval_constraints(problem: CTIRProblem, states: StateBatch) -> tuple[tuple[float, ...], ...]:
    """Evaluate sparse linear constraint responses for each state."""

    _validate_state_batch(problem, states)
    linear = _require_linear(problem)
    rows: list[tuple[float, ...]] = []
    for state in states.x:
        response: list[float] = []
        for row in range(linear.n_rows):
            start = linear.row_ptr[row]
            end = linear.row_ptr[row + 1]
            total = 0.0
            for idx in range(start, end):
                total += linear.coeff[idx] * state[linear.col_idx[idx]]
            response.append(total)
        rows.append(tuple(response))
    return tuple(rows)


def rectify_violations(
    problem: CTIRProblem,
    responses: tuple[tuple[float, ...], ...],
) -> tuple[tuple[float, ...], ...]:
    """Convert row responses into nonnegative violation magnitudes."""

    linear = _require_linear(problem)
    violations: list[tuple[float, ...]] = []
    for response in responses:
        if len(response) != linear.n_rows:
            raise ValueError("response row length must equal linear constraint count")
        row_violations: list[float] = []
        for value, rhs, sense in zip(response, linear.rhs, linear.sense):
            if sense == "<=":
                row_violations.append(max(0.0, value - rhs))
            elif sense == ">=":
                row_violations.append(max(0.0, rhs - value))
            elif sense == "==":
                row_violations.append(abs(value - rhs))
            else:
                raise ValueError(f"unsupported row sense: {sense}")
        violations.append(tuple(row_violations))
    return tuple(violations)


def reduce_penalty(
    problem: CTIRProblem,
    violations: tuple[tuple[float, ...], ...],
) -> tuple[float, ...]:
    """Reduce weighted violations into one penalty per state."""

    linear = _require_linear(problem)
    penalties: list[float] = []
    for row in violations:
        if len(row) != linear.n_rows:
            raise ValueError("violation row length must equal linear constraint count")
        penalties.append(sum(value * weight for value, weight in zip(row, linear.weight)))
    return tuple(penalties)


def objective_values(problem: CTIRProblem, states: StateBatch) -> tuple[float, ...]:
    """Evaluate the linear objective for each state."""

    _validate_state_batch(problem, states)
    coeff = problem.objective.coeff
    return tuple(sum(c * x for c, x in zip(coeff, state)) for state in states.x)


def generate_moves(problem: CTIRProblem, states: StateBatch) -> tuple[tuple[Move, ...], ...]:
    """Generate candidate bit-flip moves for each state."""

    _validate_state_batch(problem, states)
    if problem.moves.move_type != "bit_flip":
        raise ValueError(f"unsupported move type: {problem.moves.move_type}")
    moves_per_state = min(problem.moves.moves_per_state, problem.domain.n_vars)
    return tuple(
        tuple(Move(state_index=state_index, var_index=var_index) for var_index in range(moves_per_state))
        for state_index in range(states.batch_size)
    )


def score_moves(
    problem: CTIRProblem,
    states: StateBatch,
    moves: tuple[tuple[Move, ...], ...],
    *,
    penalty_weight: float = 10.0,
) -> tuple[tuple[ScoredMove, ...], ...]:
    """Score every generated move by post-move energy."""

    _validate_state_batch(problem, states)
    current_objectives = objective_values(problem, states)
    current_penalties = reduce_penalty(problem, rectify_violations(problem, eval_constraints(problem, states)))
    scored: list[tuple[ScoredMove, ...]] = []
    for state_moves in moves:
        scored_state: list[ScoredMove] = []
        for move in state_moves:
            state = list(states.x[move.state_index])
            state[move.var_index] = 1 - state[move.var_index]
            candidate = StateBatch((tuple(state),))
            objective = objective_values(problem, candidate)[0]
            penalty = reduce_penalty(
                problem,
                rectify_violations(problem, eval_constraints(problem, candidate)),
            )[0]
            energy = objective + penalty_weight * penalty
            current_energy = (
                current_objectives[move.state_index]
                + penalty_weight * current_penalties[move.state_index]
            )
            scored_state.append(
                ScoredMove(
                    move=move,
                    energy=energy,
                    objective=objective,
                    penalty=penalty,
                    improves=energy < current_energy,
                )
            )
        scored.append(tuple(scored_state))
    return tuple(scored)


def select_moves(scored: tuple[tuple[ScoredMove, ...], ...]) -> tuple[Move | None, ...]:
    """Select the best improving move for each state."""

    selected: list[Move | None] = []
    for state_moves in scored:
        improving = [entry for entry in state_moves if entry.improves]
        if not improving:
            selected.append(None)
            continue
        best = min(improving, key=lambda entry: (entry.energy, entry.penalty, entry.objective, entry.move.var_index))
        selected.append(best.move)
    return tuple(selected)


def apply_moves(states: StateBatch, selected: tuple[Move | None, ...]) -> StateBatch:
    """Apply selected bit-flip moves."""

    if len(selected) != states.batch_size:
        raise ValueError("selected move count must equal batch size")
    next_states: list[tuple[int, ...]] = []
    for state_index, state in enumerate(states.x):
        move = selected[state_index]
        updated = list(state)
        if move is not None:
            if move.state_index != state_index:
                raise ValueError("selected move state index mismatch")
            updated[move.var_index] = 1 - updated[move.var_index]
        next_states.append(tuple(updated))
    return StateBatch(tuple(next_states))


def apply_projection(problem: CTIRProblem, states: StateBatch) -> StateBatch:
    """Project states back into the declared domain."""

    if problem.projection.rules != ("binary",):
        raise ValueError(f"unsupported projection rules: {problem.projection.rules}")
    projected = tuple(tuple(1 if value >= 1 else 0 for value in state) for state in states.x)
    result = StateBatch(projected)
    _validate_state_batch(problem, result)
    return result


def reduce_best(
    problem: CTIRProblem,
    states: StateBatch,
    objectives: tuple[float, ...],
    penalties: tuple[float, ...],
    *,
    penalty_weight: float = 10.0,
) -> tuple[tuple[int, ...], float, float]:
    """Select the best feasible state when present, otherwise the best energy state."""

    _validate_state_batch(problem, states)
    if len(objectives) != states.batch_size or len(penalties) != states.batch_size:
        raise ValueError("objective and penalty counts must equal batch size")
    ranked = []
    for index, (objective, penalty) in enumerate(zip(objectives, penalties)):
        feasible_rank = 0 if penalty == 0.0 else 1
        energy = objective + penalty_weight * penalty
        ranked.append((feasible_rank, energy, penalty, objective, index))
    _, _, penalty, objective, index = min(ranked)
    return states.x[index], objective, penalty


def record_metrics(
    problem: CTIRProblem,
    iteration: int,
    states: StateBatch,
    objectives: tuple[float, ...],
    penalties: tuple[float, ...],
    violations: tuple[tuple[float, ...], ...],
    *,
    penalty_weight: float = 10.0,
) -> LedgerRow:
    """Create one validation ledger row from current runtime tensors."""

    _, objective, penalty = reduce_best(
        problem,
        states,
        objectives,
        penalties,
        penalty_weight=penalty_weight,
    )
    feasible_count = sum(1 for value in penalties if value == 0.0)
    active_violation_count = sum(1 for row in violations for value in row if value > 0.0)
    return LedgerRow(
        iteration=iteration,
        objective=objective,
        penalty=penalty,
        feasible_count=feasible_count,
        active_violation_count=active_violation_count,
    )


def _require_linear(problem: CTIRProblem):
    if problem.linear_csr is None:
        raise ValueError("CPU runtime currently requires linear_csr constraints")
    return problem.linear_csr


def _validate_state_batch(problem: CTIRProblem, states: StateBatch) -> None:
    if states.batch_size == 0:
        raise ValueError("state batch must not be empty")
    if states.n_vars != problem.domain.n_vars:
        raise ValueError("state width must equal domain.n_vars")
    for state in states.x:
        if len(state) != problem.domain.n_vars:
            raise ValueError("all states must have width domain.n_vars")
        if any(value not in (0, 1) for value in state):
            raise ValueError("CPU runtime currently supports binary states only")
