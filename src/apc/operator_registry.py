"""Operator registry for public APC runtimes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OperatorSpec:
    """One registered operator boundary."""

    name: str
    backend: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    status: str
    cpu_reference: str | None = None
    cuda_symbol: str | None = None


def default_operator_registry() -> tuple[OperatorSpec, ...]:
    """Return the current public operator registry."""

    return (
        OperatorSpec(
            name="eval_constraints",
            backend="cpu",
            inputs=("state.candidate_major", "linear.csr"),
            outputs=("constraint.response_dense",),
            status="implemented",
            cpu_reference="apc.operators_cpu.eval_constraints",
            cuda_symbol="apc_eval_linear_csr",
        ),
        OperatorSpec(
            name="rectify_violations",
            backend="cpu",
            inputs=("constraint.response_dense", "linear.csr"),
            outputs=("violation.dense",),
            status="implemented",
            cpu_reference="apc.operators_cpu.rectify_violations",
            cuda_symbol="apc_rectify_linear_violation",
        ),
        OperatorSpec(
            name="reduce_penalty",
            backend="cpu",
            inputs=("violation.dense", "linear.csr"),
            outputs=("ledger.dense",),
            status="implemented",
            cpu_reference="apc.operators_cpu.reduce_penalty",
            cuda_symbol="apc_reduce_weighted_penalty",
        ),
        OperatorSpec(
            name="eval_clauses",
            backend="cpu",
            inputs=("state.candidate_major", "clause.csr"),
            outputs=("clause.unsatisfied_dense",),
            status="implemented",
            cpu_reference="apc.readings.maxsat.eval_unsatisfied_clauses",
            cuda_symbol="apc_eval_clause_csr",
        ),
        OperatorSpec(
            name="generate_moves",
            backend="cpu",
            inputs=("state.candidate_major",),
            outputs=("move.bit_flip",),
            status="implemented",
            cpu_reference="apc.operators_cpu.generate_moves",
        ),
        OperatorSpec(
            name="score_moves",
            backend="cpu",
            inputs=("state.candidate_major", "move.bit_flip"),
            outputs=("move.score_dense",),
            status="implemented",
            cpu_reference="apc.operators_cpu.score_moves",
        ),
        OperatorSpec(
            name="select_moves",
            backend="cpu",
            inputs=("move.score_dense",),
            outputs=("move.selected",),
            status="implemented",
            cpu_reference="apc.operators_cpu.select_moves",
        ),
        OperatorSpec(
            name="apply_moves",
            backend="cpu",
            inputs=("state.candidate_major", "move.selected"),
            outputs=("state.candidate_major",),
            status="implemented",
            cpu_reference="apc.operators_cpu.apply_moves",
        ),
        OperatorSpec(
            name="apply_projection",
            backend="cpu",
            inputs=("state.candidate_major",),
            outputs=("state.candidate_major",),
            status="implemented",
            cpu_reference="apc.operators_cpu.apply_projection",
            cuda_symbol="apc_project_binary",
        ),
        OperatorSpec(
            name="reduce_best",
            backend="cpu",
            inputs=("state.candidate_major", "ledger.dense"),
            outputs=("best.candidate",),
            status="implemented",
            cpu_reference="apc.operators_cpu.reduce_best",
        ),
        OperatorSpec(
            name="record_metrics",
            backend="cpu",
            inputs=("ledger.dense", "violation.active_compact"),
            outputs=("validation.ledger",),
            status="implemented",
            cpu_reference="apc.operators_cpu.record_metrics",
        ),
    )


def registry_summary(registry: tuple[OperatorSpec, ...] | None = None) -> dict[str, Any]:
    """Return a JSON-ready registry summary."""

    rows = registry if registry is not None else default_operator_registry()
    return {
        "operators": [
            {
                "name": operator.name,
                "backend": operator.backend,
                "inputs": list(operator.inputs),
                "outputs": list(operator.outputs),
                "status": operator.status,
                "cpu_reference": operator.cpu_reference,
                "cuda_symbol": operator.cuda_symbol,
            }
            for operator in rows
        ],
        "backends": sorted(set(operator.backend for operator in rows)),
        "cuda_symbols": sorted(
            operator.cuda_symbol for operator in rows if operator.cuda_symbol is not None
        ),
    }
