"""Small CTIR-style data objects for the binary MILP repair example.

This module mirrors the theory-layer split:

L5 problem reading: binary MILP feasibility repair.
L6 CTIR: domain, LinearCSR, StateBatch, ledger config.
L8 operators: eval, reduce, score, project.
L9 validation: invariants and CPU reference tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BinaryDomain:
    """Binary state domain x in {0,1}^n."""

    n_vars: int


@dataclass(frozen=True)
class LinearCSR:
    """Linear constraints in CSR form.

    Each row is interpreted by `sense`:
    - "<=": sum(coeff * x[col]) <= rhs
    - ">=": sum(coeff * x[col]) >= rhs
    - "==": sum(coeff * x[col]) == rhs
    """

    n_rows: int
    n_vars: int
    row_ptr: tuple[int, ...]
    col_idx: tuple[int, ...]
    coeff: tuple[float, ...]
    rhs: tuple[float, ...]
    sense: tuple[str, ...]
    weight: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.row_ptr) != self.n_rows + 1:
            raise ValueError("row_ptr length must be n_rows + 1")
        if self.row_ptr[0] != 0:
            raise ValueError("row_ptr must start at 0")
        if self.row_ptr[-1] != len(self.col_idx):
            raise ValueError("row_ptr[-1] must equal nnz")
        if len(self.col_idx) != len(self.coeff):
            raise ValueError("col_idx and coeff must have the same length")
        if len(self.rhs) != self.n_rows:
            raise ValueError("rhs length must equal n_rows")
        if len(self.sense) != self.n_rows:
            raise ValueError("sense length must equal n_rows")
        if len(self.weight) != self.n_rows:
            raise ValueError("weight length must equal n_rows")
        invalid = [s for s in self.sense if s not in ("<=", ">=", "==")]
        if invalid:
            raise ValueError(f"invalid sense values: {invalid}")


@dataclass(frozen=True)
class StateBatch:
    """Candidate-major state batch X[B,n]."""

    x: tuple[tuple[int, ...], ...]

    @property
    def batch_size(self) -> int:
        return len(self.x)

    @property
    def n_vars(self) -> int:
        return len(self.x[0]) if self.x else 0


@dataclass(frozen=True)
class RepairConfig:
    """Controls the repair feedback loop."""

    max_iters: int = 16
    lambda_penalty: float = 10.0
    objective_weight: float = 1.0

