"""Materialize planned host layouts."""

from __future__ import annotations

from dataclasses import dataclass

from .ctir import LinearCSR, StateBatch
from .layout import (
    CANDIDATE_MAJOR,
    LINEAR_CSC,
    LINEAR_CSR,
    VARIABLE_MAJOR,
    VIOLATION_ACTIVE,
    VIOLATION_DENSE,
)
from .layout_ledger import LayoutCost


@dataclass(frozen=True)
class MaterializedLayout:
    """One materialized host layout plus its conversion cost."""

    name: str
    data: object
    cost: LayoutCost


@dataclass(frozen=True)
class LinearCSC:
    """Column-major sparse linear incidence view."""

    n_rows: int
    n_vars: int
    col_ptr: tuple[int, ...]
    row_idx: tuple[int, ...]
    coeff: tuple[float, ...]

    @property
    def nnz(self) -> int:
        return len(self.row_idx)


@dataclass(frozen=True)
class ActiveViolationCompact:
    """Compact active violation coordinates."""

    batch_size: int
    n_constraints: int
    entries: tuple[tuple[int, int, float], ...]


def materialize_variable_major(states: StateBatch) -> MaterializedLayout:
    """Materialize X_t[n_vars, batch_size] from candidate-major states."""

    if states.batch_size == 0 or states.n_vars == 0:
        raise ValueError("state batch must not be empty")
    transposed = tuple(
        tuple(states.x[batch][var] for batch in range(states.batch_size))
        for var in range(states.n_vars)
    )
    elements = states.batch_size * states.n_vars
    return MaterializedLayout(
        name=VARIABLE_MAJOR,
        data=transposed,
        cost=LayoutCost(
            source=CANDIDATE_MAJOR,
            target=VARIABLE_MAJOR,
            elements_read=elements,
            elements_written=elements,
            reason="materialize variable-major state view",
        ),
    )


def materialize_linear_csc(linear: LinearCSR) -> MaterializedLayout:
    """Materialize CSC / incidence view from LinearCSR."""

    counts = [0 for _ in range(linear.n_vars)]
    for col in linear.col_idx:
        counts[col] += 1

    col_ptr = [0]
    for count in counts:
        col_ptr.append(col_ptr[-1] + count)

    next_slot = col_ptr[:-1].copy()
    row_idx = [0 for _ in range(linear.nnz)]
    coeff = [0.0 for _ in range(linear.nnz)]
    for row in range(linear.n_rows):
        for offset in range(linear.row_ptr[row], linear.row_ptr[row + 1]):
            col = linear.col_idx[offset]
            slot = next_slot[col]
            row_idx[slot] = row
            coeff[slot] = linear.coeff[offset]
            next_slot[col] += 1

    csc = LinearCSC(
        n_rows=linear.n_rows,
        n_vars=linear.n_vars,
        col_ptr=tuple(col_ptr),
        row_idx=tuple(row_idx),
        coeff=tuple(coeff),
    )
    return MaterializedLayout(
        name=LINEAR_CSC,
        data=csc,
        cost=LayoutCost(
            source=LINEAR_CSR,
            target=LINEAR_CSC,
            elements_read=linear.nnz,
            elements_written=linear.nnz,
            reason="materialize sparse variable incidence view",
        ),
    )


def materialize_active_violations(violations: tuple[tuple[float, ...], ...]) -> MaterializedLayout:
    """Materialize compact active violation coordinates."""

    if len(violations) == 0:
        raise ValueError("violations must not be empty")
    n_constraints = len(violations[0])
    entries: list[tuple[int, int, float]] = []
    for batch, row in enumerate(violations):
        if len(row) != n_constraints:
            raise ValueError("all violation rows must have the same width")
        for constraint, value in enumerate(row):
            if value > 0.0:
                entries.append((batch, constraint, value))

    elements = len(violations) * n_constraints
    compact = ActiveViolationCompact(
        batch_size=len(violations),
        n_constraints=n_constraints,
        entries=tuple(entries),
    )
    return MaterializedLayout(
        name=VIOLATION_ACTIVE,
        data=compact,
        cost=LayoutCost(
            source=VIOLATION_DENSE,
            target=VIOLATION_ACTIVE,
            elements_read=elements,
            elements_written=len(entries),
            reason="materialize active violation coordinates",
        ),
    )
