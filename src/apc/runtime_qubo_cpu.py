"""QUBO CPU reference execution contract.

This module defines and runs the public QUBO CPU reference route.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .branch_tensor import branch_tensor_from_state_pool
from .ctir import CTIRProblem, StateBatch
from .operators_cpu import Move, apply_moves, apply_projection, generate_moves
from .operator_call_ledger import describe_contract_call_ledger
from .readings.qubo import load_qubo_json, lower_qubo_to_ctir
from .runtime_contract import RuntimeExecutionContract, RuntimeStepSpec, runtime_contract_to_dict
from .runtime_status import FAILED, IMPLEMENTED, PLANNED
from .state_pool import StatePool, state_pool_with_scores


QUBO_LEDGER_FIELDS = (
    "objective",
    "penalty",
    "energy",
    "move_count",
    "final_state",
)


def default_qubo_cpu_reference_contract() -> RuntimeExecutionContract:
    """Return the public QUBO CPU reference contract."""

    return RuntimeExecutionContract(
        name="qubo_cpu_reference_runtime",
        version="apc.qubo_cpu_reference_contract.v1",
        backend="cpu",
        problem_families=("qubo",),
        steps=(
            RuntimeStepSpec(
                name="load_qubo_spec",
                kind="load",
                inputs=("problem.spec",),
                outputs=("qubo.spec",),
                status="implemented",
                timing_fields=("end_to_end_time_s",),
                notes=("Only the public binary QUBO spec shape is accepted.",),
            ),
            RuntimeStepSpec(
                name="lower_qubo_to_ctir",
                kind="lowering",
                inputs=("qubo.spec",),
                outputs=("ctir.problem", "ctir.qubo_coo"),
                status="implemented",
                timing_fields=("end_to_end_time_s",),
                notes=("Linear and quadratic terms remain explicit in CTIR metadata.",),
            ),
            RuntimeStepSpec(
                name="initialize_binary_state_pool",
                kind="state_pool",
                inputs=("ctir.problem", "runtime.config"),
                outputs=("state.pool", "state.candidate_major"),
                status=IMPLEMENTED,
                timing_fields=("end_to_end_time_s",),
            ),
            RuntimeStepSpec(
                name="evaluate_qubo_energy",
                kind="operator",
                inputs=("ctir.qubo_coo", "ctir.objective_linear", "state.candidate_major"),
                outputs=("energy.dense",),
                status=IMPLEMENTED,
                operator_name="eval_qubo_energy",
            ),
            RuntimeStepSpec(
                name="generate_bitflip_moves",
                kind="branch_tensor",
                inputs=("ctir.problem", "state.pool"),
                outputs=("branch.tensor",),
                status=IMPLEMENTED,
                operator_name="generate_moves",
            ),
            RuntimeStepSpec(
                name="score_qubo_bitflip_moves",
                kind="operator",
                inputs=("ctir.qubo_coo", "state.candidate_major", "branch.tensor"),
                outputs=("branch.score_dense",),
                status=IMPLEMENTED,
                operator_name="score_qubo_bitflip_moves",
            ),
            RuntimeStepSpec(
                name="select_reduction_gate_actions",
                kind="reduction_gate",
                inputs=("branch.score_dense", "branch.tensor"),
                outputs=("action.selected",),
                status=IMPLEMENTED,
                operator_name="select_moves",
            ),
            RuntimeStepSpec(
                name="apply_selected_actions",
                kind="operator",
                inputs=("state.candidate_major", "action.selected"),
                outputs=("state.candidate_major",),
                status=IMPLEMENTED,
                operator_name="apply_moves",
            ),
            RuntimeStepSpec(
                name="project_binary_domain",
                kind="operator",
                inputs=("ctir.problem", "state.candidate_major"),
                outputs=("state.candidate_major",),
                status=IMPLEMENTED,
                operator_name="apply_projection",
            ),
            RuntimeStepSpec(
                name="record_qubo_ledger",
                kind="ledger",
                inputs=("state.candidate_major", "energy.dense", "branch.tensor"),
                outputs=("validation.ledger",),
                status=IMPLEMENTED,
                operator_name="record_metrics",
                notes=(f"Ledger fields: {', '.join(QUBO_LEDGER_FIELDS)}.",),
            ),
            RuntimeStepSpec(
                name="project_public_summary",
                kind="interface_projection",
                inputs=("state.pool", "validation.ledger", "best.candidate"),
                outputs=("public.runtime_summary",),
                status=IMPLEMENTED,
                timing_fields=("end_to_end_time_s",),
            ),
        ),
        non_goals=(
            "QUBO optimality proof is outside this CPU reference contract.",
            "Drop-in solver API replacement is outside this CPU reference contract.",
            "CUDA parity is gated on this CPU reference contract and later execution evidence.",
            "Performance claims require complete timing evidence.",
        ),
    )


def describe_qubo_cpu_reference_contract() -> dict[str, Any]:
    """Return a JSON-ready QUBO CPU reference contract report."""

    contract = default_qubo_cpu_reference_contract()
    return {
        **runtime_contract_to_dict(contract),
        "execution_status": IMPLEMENTED,
        "ledger_fields": list(QUBO_LEDGER_FIELDS),
        "notes": [
            "This is the QUBO CPU reference execution contract and public route surface.",
            "Deterministic CPU behavior exists before CUDA QUBO parity is added.",
            "The contract does not imply solver API compatibility.",
        ],
    }


def describe_qubo_cpu_reference_contract_from_json(
    path: str | Path,
    *,
    batch_size: int = 4,
) -> dict[str, Any]:
    """Return a QUBO CPU reference contract report for one public spec."""

    try:
        spec = load_qubo_json(path)
        problem = lower_qubo_to_ctir(spec, batch_size=batch_size)
    except Exception as exc:
        return {
            "schema": "apc.qubo_cpu_reference_contract.v1",
            "status": FAILED,
            "execution_status": IMPLEMENTED,
            "source_path": str(path),
            "problem_family": "qubo",
            "reason": str(exc),
            "notes": [
                "Unsupported QUBO inputs fail before execution.",
                "The QUBO CPU reference execution route accepts only the public QUBO spec shape.",
            ],
        }

    contract = default_qubo_cpu_reference_contract()
    contract_payload = describe_qubo_cpu_reference_contract()
    return {
        **contract_payload,
        "status": "implemented",
        "source_path": str(path),
        "problem_family": "qubo",
        "config": {
            "batch_size": batch_size,
            "moves_per_state": problem.moves.moves_per_state,
        },
        "ctir": {
            "n_vars": problem.domain.n_vars,
            "qubo_nnz": len(problem.qubo_coo.q) if problem.qubo_coo is not None else 0,
            "linear_terms": list(problem.objective.coeff),
        },
        "call_ledger_shape": describe_contract_call_ledger(contract),
    }


@dataclass(frozen=True)
class QUBORuntimeConfig:
    """Controls for the deterministic QUBO CPU reference route."""

    max_iters: int = 8
    batch_size: int = 4
    seed: int = 0

    def __post_init__(self) -> None:
        if self.max_iters < 0:
            raise ValueError("max_iters must be nonnegative")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")


@dataclass(frozen=True)
class QUBOLedgerRow:
    """One public QUBO runtime ledger row."""

    iteration: int
    objective: float
    penalty: float
    energy: float
    move_count: int
    final_state: tuple[int, ...]


@dataclass(frozen=True)
class QUBORuntimeResult:
    """Output of the QUBO CPU reference route."""

    best_state: tuple[int, ...]
    best_objective: float
    best_penalty: float
    best_energy: float
    move_count: int
    ledger: tuple[QUBOLedgerRow, ...]
    final_states: StateBatch


@dataclass(frozen=True)
class QUBOScoredMove:
    """QUBO move score computed from post-move energy."""

    move: Move
    objective: float
    penalty: float
    energy: float
    improves: bool


def run_qubo_cpu_reference(
    problem: CTIRProblem,
    *,
    config: QUBORuntimeConfig | None = None,
    initial_states: StateBatch | None = None,
) -> QUBORuntimeResult:
    """Run the deterministic QUBO CPU reference route."""

    _require_qubo(problem)
    cfg = config or QUBORuntimeConfig(batch_size=problem.moves.batch_size)
    states = initial_states if initial_states is not None else _initial_states(problem, cfg)
    states = apply_projection(problem, states)

    ledger: list[QUBOLedgerRow] = []
    best_state: tuple[int, ...] | None = None
    best_objective = 0.0
    best_energy = 0.0
    move_count = 0

    for iteration in range(cfg.max_iters + 1):
        energies = eval_qubo_energy(problem, states)
        pool = _state_pool_from_states(states, energies, origin=f"iteration_{iteration}")
        best_index = _best_energy_index(energies, states)
        candidate_state = states.x[best_index]
        candidate_energy = energies[best_index]
        candidate_objective = candidate_energy
        if best_state is None or _energy_rank(candidate_energy, candidate_state) < _energy_rank(
            best_energy,
            best_state,
        ):
            best_state = candidate_state
            best_objective = candidate_objective
            best_energy = candidate_energy

        ledger.append(
            QUBOLedgerRow(
                iteration=iteration,
                objective=best_objective,
                penalty=0.0,
                energy=best_energy,
                move_count=move_count,
                final_state=best_state,
            )
        )

        if iteration == cfg.max_iters:
            break

        tensor = branch_tensor_from_state_pool(problem, pool)
        scored = score_qubo_bitflip_moves(problem, pool, tensor)
        selected = select_qubo_bitflip_moves(scored)
        next_states = apply_projection(problem, apply_moves(states, selected))
        applied_count = sum(1 for move in selected if move is not None)
        move_count += applied_count
        if applied_count == 0 or next_states == states:
            continue
        states = next_states

    if best_state is None:
        raise RuntimeError("QUBO runtime did not evaluate any states")
    return QUBORuntimeResult(
        best_state=best_state,
        best_objective=best_objective,
        best_penalty=0.0,
        best_energy=best_energy,
        move_count=move_count,
        ledger=tuple(ledger),
        final_states=states,
    )


def run_qubo_cpu_reference_from_json(
    path: str | Path,
    *,
    config: QUBORuntimeConfig | None = None,
    initial_states: StateBatch | None = None,
) -> QUBORuntimeResult:
    """Load a QUBO JSON spec, lower it to CTIR, and run the CPU reference route."""

    cfg = config or QUBORuntimeConfig()
    spec = load_qubo_json(path)
    problem = lower_qubo_to_ctir(spec, batch_size=cfg.batch_size)
    return run_qubo_cpu_reference(problem, config=cfg, initial_states=initial_states)


def describe_qubo_cpu_reference_execution_from_json(
    path: str | Path,
    *,
    config: QUBORuntimeConfig | None = None,
) -> dict[str, Any]:
    """Return a JSON-ready QUBO CPU reference execution report."""

    cfg = config or QUBORuntimeConfig()
    try:
        result = run_qubo_cpu_reference_from_json(path, config=cfg)
    except Exception as exc:
        return {
            "schema": "apc.qubo_cpu_reference_execution.v1",
            "status": FAILED,
            "source_path": str(path),
            "problem_family": "qubo",
            "backend": "cpu",
            "reason": str(exc),
        }
    return qubo_runtime_result_to_dict(result, source_path=str(path), config=cfg)


def eval_qubo_energy(problem: CTIRProblem, states: StateBatch) -> tuple[float, ...]:
    """Evaluate QUBO energy for each candidate state."""

    qubo = _require_qubo(problem)
    _validate_state_batch(problem, states)
    energies: list[float] = []
    for state in states.x:
        linear = sum(coeff * value for coeff, value in zip(problem.objective.coeff, state))
        quadratic = sum(weight * state[i] * state[j] for i, j, weight in zip(qubo.i, qubo.j, qubo.q))
        energies.append(linear + quadratic)
    return tuple(energies)


def score_qubo_bitflip_moves(
    problem: CTIRProblem,
    pool: StatePool,
    tensor,
) -> tuple[tuple[QUBOScoredMove, ...], ...]:
    """Score every alive QUBO bit-flip move by post-move energy."""

    current_energies = eval_qubo_energy(problem, pool.states)
    scored_rows: list[tuple[QUBOScoredMove, ...]] = []
    for state_index, row in enumerate(tensor.routes):
        scored_row: list[QUBOScoredMove] = []
        for route_index, route in enumerate(row):
            move = Move(state_index=route.state_index, var_index=route.payload[0])
            if not tensor.alive_mask[state_index][route_index]:
                scored_row.append(
                    QUBOScoredMove(
                        move=move,
                        objective=current_energies[state_index],
                        penalty=0.0,
                        energy=current_energies[state_index],
                        improves=False,
                    )
                )
                continue
            state = list(pool.states.x[route.state_index])
            state[move.var_index] = 1 - state[move.var_index]
            energy = eval_qubo_energy(problem, StateBatch((tuple(state),)))[0]
            scored_row.append(
                QUBOScoredMove(
                    move=move,
                    objective=energy,
                    penalty=0.0,
                    energy=energy,
                    improves=energy < current_energies[route.state_index],
                )
            )
        scored_rows.append(tuple(scored_row))
    return tuple(scored_rows)


def select_qubo_bitflip_moves(
    scored: tuple[tuple[QUBOScoredMove, ...], ...],
) -> tuple[Move | None, ...]:
    """Select the best improving QUBO move for each state."""

    selected: list[Move | None] = []
    for row in scored:
        improving = [entry for entry in row if entry.improves]
        if not improving:
            selected.append(None)
            continue
        best = min(improving, key=lambda entry: (entry.energy, entry.move.var_index))
        selected.append(best.move)
    return tuple(selected)


def qubo_runtime_result_to_dict(
    result: QUBORuntimeResult,
    *,
    source_path: str | None = None,
    config: QUBORuntimeConfig | None = None,
) -> dict[str, Any]:
    """Serialize a QUBO runtime result as a public summary."""

    payload: dict[str, Any] = {
        "schema": "apc.qubo_cpu_reference_execution.v1",
        "status": "implemented",
        "execution_status": IMPLEMENTED,
        "backend": "cpu",
        "problem_family": "qubo",
        "best": {
            "objective": result.best_objective,
            "penalty": result.best_penalty,
            "energy": result.best_energy,
            "state": list(result.best_state),
        },
        "move_count": result.move_count,
        "final_state": list(result.best_state),
        "ledger_fields": list(QUBO_LEDGER_FIELDS),
        "ledger": qubo_ledger_to_dicts(result.ledger),
        "final_states": [list(row) for row in result.final_states.x],
        "notes": [
            "This is deterministic CPU reference evidence, not a solver-compatibility claim.",
            "CUDA QUBO parity should compare against this route.",
        ],
    }
    if source_path is not None:
        payload["source_path"] = source_path
    if config is not None:
        payload["config"] = {
            "max_iters": config.max_iters,
            "batch_size": config.batch_size,
            "seed": config.seed,
        }
    return payload


def qubo_ledger_to_dicts(rows: tuple[QUBOLedgerRow, ...]) -> list[dict[str, Any]]:
    """Convert QUBO ledger rows into JSON-ready dictionaries."""

    return [
        {
            "iteration": row.iteration,
            "objective": row.objective,
            "penalty": row.penalty,
            "energy": row.energy,
            "move_count": row.move_count,
            "final_state": list(row.final_state),
        }
        for row in rows
    ]


def _initial_states(problem: CTIRProblem, config: QUBORuntimeConfig) -> StateBatch:
    rng = random.Random(config.seed)
    states = []
    for row in range(config.batch_size):
        if row == 0:
            states.append(tuple(0 for _ in range(problem.domain.n_vars)))
        else:
            states.append(tuple(rng.randint(0, 1) for _ in range(problem.domain.n_vars)))
    return StateBatch(tuple(states))


def _state_pool_from_states(states: StateBatch, energies: tuple[float, ...], *, origin: str) -> StatePool:
    return state_pool_with_scores(
        StatePool(
            states=states,
            scores=tuple(0.0 for _ in states.x),
            uncertainty=tuple(0.0 for _ in states.x),
            alive_mask=tuple(True for _ in states.x),
            metadata=tuple({"origin": origin, "row": row} for row in range(states.batch_size)),
        ),
        energies,
    )


def _best_energy_index(energies: tuple[float, ...], states: StateBatch) -> int:
    ranked = [(_energy_rank(energy, states.x[index]), index) for index, energy in enumerate(energies)]
    return min(ranked)[1]


def _energy_rank(energy: float, state: tuple[int, ...]) -> tuple[float, tuple[int, ...]]:
    return (energy, state)


def _require_qubo(problem: CTIRProblem):
    if problem.qubo_coo is None:
        raise ValueError("QUBO CPU runtime requires qubo_coo")
    return problem.qubo_coo


def _validate_state_batch(problem: CTIRProblem, states: StateBatch) -> None:
    if states.batch_size == 0:
        raise ValueError("state batch must not be empty")
    if states.n_vars != problem.domain.n_vars:
        raise ValueError("state width must equal domain.n_vars")
    for state in states.x:
        if len(state) != problem.domain.n_vars:
            raise ValueError("all states must have width domain.n_vars")
        if any(value not in (0, 1) for value in state):
            raise ValueError("QUBO CPU runtime currently supports binary states only")
