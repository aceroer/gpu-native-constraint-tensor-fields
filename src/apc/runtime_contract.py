"""Public runtime execution contract descriptions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_TIMING_FIELDS = (
    "kernel_time_s",
    "copy_time_s",
    "layout_conversion_time_s",
    "end_to_end_time_s",
)


@dataclass(frozen=True)
class RuntimeStepSpec:
    """One public runtime execution step."""

    name: str
    kind: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    status: str
    timing_fields: tuple[str, ...] = DEFAULT_TIMING_FIELDS
    operator_name: str | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("RuntimeStepSpec.name must not be empty")
        if not self.kind:
            raise ValueError("RuntimeStepSpec.kind must not be empty")
        if not self.inputs:
            raise ValueError(f"{self.name} must name at least one input")
        if not self.outputs:
            raise ValueError(f"{self.name} must name at least one output")
        if self.status not in {"implemented", "planned", "skipped"}:
            raise ValueError(f"{self.name} has unsupported status")
        if not self.timing_fields:
            raise ValueError(f"{self.name} must expose timing fields")
        for field in self.timing_fields:
            if not field.endswith("_s"):
                raise ValueError(f"{self.name} timing field must end with _s")


@dataclass(frozen=True)
class RuntimeExecutionContract:
    """A public execution contract for a runtime path."""

    name: str
    version: str
    backend: str
    problem_families: tuple[str, ...]
    steps: tuple[RuntimeStepSpec, ...]
    non_goals: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("RuntimeExecutionContract.name must not be empty")
        if not self.version:
            raise ValueError("RuntimeExecutionContract.version must not be empty")
        if not self.backend:
            raise ValueError("RuntimeExecutionContract.backend must not be empty")
        if not self.problem_families:
            raise ValueError("RuntimeExecutionContract must name problem families")
        if not self.steps:
            raise ValueError("RuntimeExecutionContract.steps must not be empty")
        names = [step.name for step in self.steps]
        if len(names) != len(set(names)):
            raise ValueError("RuntimeExecutionContract step names must be unique")


def default_runtime_execution_contract() -> RuntimeExecutionContract:
    """Return the current public CPU repair runtime execution contract."""

    return RuntimeExecutionContract(
        name="cpu_repair_runtime",
        version="apc.runtime_execution_contract.v1",
        backend="cpu",
        problem_families=("binary_milp", "maxsat"),
        steps=(
            RuntimeStepSpec(
                name="lower_problem_to_ctir",
                kind="lowering",
                inputs=("problem.spec",),
                outputs=("ctir.problem",),
                status="implemented",
                timing_fields=("end_to_end_time_s",),
                notes=("JSON specs lower into inspectable CTIR before execution.",),
            ),
            RuntimeStepSpec(
                name="materialize_layouts",
                kind="layout",
                inputs=("ctir.problem", "state.candidate_major"),
                outputs=("layout.plan", "layout.cost_ledger"),
                status="implemented",
                timing_fields=("layout_conversion_time_s", "end_to_end_time_s"),
                notes=("Layout conversion costs remain explicit.",),
            ),
            RuntimeStepSpec(
                name="initialize_state_pool",
                kind="state_pool",
                inputs=("ctir.problem", "runtime.config"),
                outputs=("state.pool",),
                status="implemented",
                timing_fields=("end_to_end_time_s",),
            ),
            RuntimeStepSpec(
                name="initial_projection",
                kind="operator",
                inputs=("ctir.problem", "state.candidate_major"),
                outputs=("state.candidate_major",),
                status="implemented",
                operator_name="apply_projection",
            ),
            RuntimeStepSpec(
                name="eval_constraints",
                kind="operator",
                inputs=("ctir.problem", "state.candidate_major"),
                outputs=("constraint.response_dense",),
                status="implemented",
                operator_name="eval_constraints",
            ),
            RuntimeStepSpec(
                name="rectify_violations",
                kind="operator",
                inputs=("ctir.problem", "constraint.response_dense"),
                outputs=("violation.dense",),
                status="implemented",
                operator_name="rectify_violations",
            ),
            RuntimeStepSpec(
                name="reduce_penalty",
                kind="operator",
                inputs=("ctir.problem", "violation.dense"),
                outputs=("ledger.dense",),
                status="implemented",
                operator_name="reduce_penalty",
            ),
            RuntimeStepSpec(
                name="record_metrics",
                kind="ledger",
                inputs=("state.candidate_major", "ledger.dense", "violation.dense"),
                outputs=("validation.ledger",),
                status="implemented",
                operator_name="record_metrics",
            ),
            RuntimeStepSpec(
                name="reduce_best",
                kind="operator",
                inputs=("state.candidate_major", "ledger.dense"),
                outputs=("best.candidate",),
                status="implemented",
                operator_name="reduce_best",
            ),
            RuntimeStepSpec(
                name="generate_branch_tensor",
                kind="branch_tensor",
                inputs=("ctir.problem", "state.pool"),
                outputs=("branch.tensor",),
                status="implemented",
                operator_name="generate_moves",
            ),
            RuntimeStepSpec(
                name="score_branches",
                kind="operator",
                inputs=("ctir.problem", "state.candidate_major", "branch.tensor"),
                outputs=("branch.score_dense",),
                status="implemented",
                operator_name="score_moves",
            ),
            RuntimeStepSpec(
                name="select_reduction_gate_actions",
                kind="reduction_gate",
                inputs=("branch.score_dense", "branch.tensor"),
                outputs=("action.selected",),
                status="implemented",
                operator_name="select_moves",
            ),
            RuntimeStepSpec(
                name="apply_selected_actions",
                kind="operator",
                inputs=("state.candidate_major", "action.selected"),
                outputs=("state.candidate_major",),
                status="implemented",
                operator_name="apply_moves",
            ),
            RuntimeStepSpec(
                name="project_public_summary",
                kind="interface_projection",
                inputs=("state.pool", "branch.tensor", "validation.ledger", "best.candidate"),
                outputs=("public.runtime_summary",),
                status="implemented",
                timing_fields=("end_to_end_time_s",),
            ),
        ),
        non_goals=(
            "Full optimality proof is outside this runtime contract.",
            "Drop-in solver API replacement is outside this runtime contract.",
            "Performance claims require complete timing evidence.",
        ),
    )


def runtime_contract_to_dict(contract: RuntimeExecutionContract) -> dict[str, Any]:
    """Serialize a runtime execution contract into JSON-ready data."""

    return {
        "schema": contract.version,
        "name": contract.name,
        "backend": contract.backend,
        "problem_families": list(contract.problem_families),
        "steps": [_step_to_dict(step) for step in contract.steps],
        "non_goals": list(contract.non_goals),
    }


def describe_cpu_runtime_contract() -> dict[str, Any]:
    """Return a JSON-ready description of the current CPU runtime path."""

    return runtime_contract_to_dict(default_runtime_execution_contract())


def _step_to_dict(step: RuntimeStepSpec) -> dict[str, Any]:
    return {
        "name": step.name,
        "kind": step.kind,
        "inputs": list(step.inputs),
        "outputs": list(step.outputs),
        "status": step.status,
        "timing_fields": list(step.timing_fields),
        "operator_name": step.operator_name,
        "notes": list(step.notes),
    }
