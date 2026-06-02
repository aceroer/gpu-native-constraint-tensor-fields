"""Operator call ledger records for runtime contract steps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .runtime_contract import RuntimeExecutionContract, RuntimeStepSpec


@dataclass(frozen=True)
class OperatorCallLedgerRow:
    """One factual call row for a runtime contract step."""

    step_name: str
    backend: str
    status: str
    timing: dict[str, float | None]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    operator_name: str | None = None

    def __post_init__(self) -> None:
        if not self.step_name:
            raise ValueError("OperatorCallLedgerRow.step_name must not be empty")
        if not self.backend:
            raise ValueError("OperatorCallLedgerRow.backend must not be empty")
        if self.status not in {"implemented", "planned", "skipped", "failed"}:
            raise ValueError(f"{self.step_name} has unsupported call status")
        if not self.inputs:
            raise ValueError(f"{self.step_name} must name inputs")
        if not self.outputs:
            raise ValueError(f"{self.step_name} must name outputs")
        if not self.timing:
            raise ValueError(f"{self.step_name} must expose timing fields")
        for field, value in self.timing.items():
            if not field.endswith("_s"):
                raise ValueError(f"{self.step_name} timing field must end with _s")
            if value is not None and value < 0.0:
                raise ValueError(f"{self.step_name} timing values must be nonnegative")


@dataclass(frozen=True)
class OperatorCallLedger:
    """A JSON-ready ledger for runtime contract step calls."""

    schema: str
    contract_schema: str
    backend: str
    rows: tuple[OperatorCallLedgerRow, ...]
    notes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema != "apc.operator_call_ledger.v1":
            raise ValueError("OperatorCallLedger schema must be apc.operator_call_ledger.v1")
        if not self.contract_schema:
            raise ValueError("OperatorCallLedger.contract_schema must not be empty")
        if not self.backend:
            raise ValueError("OperatorCallLedger.backend must not be empty")
        if not self.rows:
            raise ValueError("OperatorCallLedger.rows must not be empty")


def call_ledger_from_contract(
    contract: RuntimeExecutionContract,
    *,
    timings: dict[str, dict[str, float]] | None = None,
    statuses: dict[str, str] | None = None,
) -> OperatorCallLedger:
    """Create a factual operator call ledger from a runtime contract."""

    timing_rows = timings or {}
    status_rows = statuses or {}
    rows = tuple(
        _row_from_step(
            step,
            backend=contract.backend,
            timing_values=timing_rows.get(step.name, {}),
            status=status_rows.get(step.name, step.status),
        )
        for step in contract.steps
    )
    return OperatorCallLedger(
        schema="apc.operator_call_ledger.v1",
        contract_schema=contract.version,
        backend=contract.backend,
        rows=rows,
        notes=(
            "Ledger rows describe runtime contract calls only.",
            "Timing values are evidence fields, not performance claims.",
            "The ledger does not imply solver API compatibility.",
        ),
    )


def operator_call_ledger_to_dict(ledger: OperatorCallLedger) -> dict[str, Any]:
    """Serialize an operator call ledger into JSON-ready data."""

    return {
        "schema": ledger.schema,
        "contract_schema": ledger.contract_schema,
        "backend": ledger.backend,
        "rows": [_row_to_dict(row) for row in ledger.rows],
        "notes": list(ledger.notes),
    }


def describe_contract_call_ledger(
    contract: RuntimeExecutionContract,
    *,
    timings: dict[str, dict[str, float]] | None = None,
    statuses: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Return a JSON-ready call ledger for a runtime execution contract."""

    return operator_call_ledger_to_dict(
        call_ledger_from_contract(contract, timings=timings, statuses=statuses)
    )


def _row_from_step(
    step: RuntimeStepSpec,
    *,
    backend: str,
    timing_values: dict[str, float],
    status: str,
) -> OperatorCallLedgerRow:
    timing = {field: timing_values.get(field) for field in step.timing_fields}
    return OperatorCallLedgerRow(
        step_name=step.name,
        backend=backend,
        status=status,
        timing=timing,
        inputs=step.inputs,
        outputs=step.outputs,
        operator_name=step.operator_name,
    )


def _row_to_dict(row: OperatorCallLedgerRow) -> dict[str, Any]:
    return {
        "step_name": row.step_name,
        "backend": row.backend,
        "status": row.status,
        "timing": dict(row.timing),
        "inputs": list(row.inputs),
        "outputs": list(row.outputs),
        "operator_name": row.operator_name,
    }
