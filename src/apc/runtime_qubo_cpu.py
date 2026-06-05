"""QUBO CPU reference execution contract.

This module defines the public contract for the future QUBO CPU reference route.
It does not execute QUBO repair yet; Phase 60 owns the executable route.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .operator_call_ledger import describe_contract_call_ledger
from .readings.qubo import load_qubo_json, lower_qubo_to_ctir
from .runtime_contract import RuntimeExecutionContract, RuntimeStepSpec, runtime_contract_to_dict
from .runtime_status import FAILED, PLANNED


QUBO_LEDGER_FIELDS = (
    "objective",
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
                status=PLANNED,
                timing_fields=("end_to_end_time_s",),
            ),
            RuntimeStepSpec(
                name="evaluate_qubo_energy",
                kind="operator",
                inputs=("ctir.qubo_coo", "ctir.objective_linear", "state.candidate_major"),
                outputs=("energy.dense",),
                status=PLANNED,
                operator_name="eval_qubo_energy",
            ),
            RuntimeStepSpec(
                name="generate_bitflip_moves",
                kind="branch_tensor",
                inputs=("ctir.problem", "state.pool"),
                outputs=("branch.tensor",),
                status=PLANNED,
                operator_name="generate_moves",
            ),
            RuntimeStepSpec(
                name="score_qubo_bitflip_moves",
                kind="operator",
                inputs=("ctir.qubo_coo", "state.candidate_major", "branch.tensor"),
                outputs=("branch.score_dense",),
                status=PLANNED,
                operator_name="score_qubo_bitflip_moves",
            ),
            RuntimeStepSpec(
                name="select_reduction_gate_actions",
                kind="reduction_gate",
                inputs=("branch.score_dense", "branch.tensor"),
                outputs=("action.selected",),
                status=PLANNED,
                operator_name="select_moves",
            ),
            RuntimeStepSpec(
                name="apply_selected_actions",
                kind="operator",
                inputs=("state.candidate_major", "action.selected"),
                outputs=("state.candidate_major",),
                status=PLANNED,
                operator_name="apply_moves",
            ),
            RuntimeStepSpec(
                name="project_binary_domain",
                kind="operator",
                inputs=("ctir.problem", "state.candidate_major"),
                outputs=("state.candidate_major",),
                status=PLANNED,
                operator_name="apply_projection",
            ),
            RuntimeStepSpec(
                name="record_qubo_ledger",
                kind="ledger",
                inputs=("state.candidate_major", "energy.dense", "branch.tensor"),
                outputs=("validation.ledger",),
                status=PLANNED,
                operator_name="record_metrics",
                notes=(f"Ledger fields: {', '.join(QUBO_LEDGER_FIELDS)}.",),
            ),
            RuntimeStepSpec(
                name="project_public_summary",
                kind="interface_projection",
                inputs=("state.pool", "validation.ledger", "best.candidate"),
                outputs=("public.runtime_summary",),
                status=PLANNED,
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
        "execution_status": PLANNED,
        "ledger_fields": list(QUBO_LEDGER_FIELDS),
        "notes": [
            "This is the QUBO CPU reference execution contract, not the executable route.",
            "Deterministic CPU behavior must exist before CUDA QUBO parity is added.",
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
            "execution_status": PLANNED,
            "source_path": str(path),
            "problem_family": "qubo",
            "reason": str(exc),
            "notes": [
                "Unsupported QUBO inputs fail before execution.",
                "The QUBO CPU reference execution route is planned for the next phase.",
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
