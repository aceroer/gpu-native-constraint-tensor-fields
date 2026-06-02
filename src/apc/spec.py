"""Native problem spec objects.

Phase 1 keeps the public input format intentionally small. The first supported
target is binary MILP feasibility repair with sparse linear constraints.
"""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_ROW_SENSES = ("<=", ">=", "==")


@dataclass(frozen=True)
class BinaryDomainSpec:
    """Binary domain x in {0,1}^n."""

    n_vars: int

    def __post_init__(self) -> None:
        if not isinstance(self.n_vars, int) or self.n_vars <= 0:
            raise ValueError("domain.n_vars must be a positive integer")


@dataclass(frozen=True)
class ObjectiveSpec:
    """Linear objective c^T x."""

    linear: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.linear) == 0:
            raise ValueError("objective.linear must not be empty")


@dataclass(frozen=True)
class LinearCSRSpec:
    """Sparse linear constraints in CSR form."""

    n_rows: int
    row_ptr: tuple[int, ...]
    col_idx: tuple[int, ...]
    coeff: tuple[float, ...]
    rhs: tuple[float, ...]
    sense: tuple[str, ...]
    weight: tuple[float, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.n_rows, int) or self.n_rows <= 0:
            raise ValueError("linear_csr.n_rows must be a positive integer")
        if len(self.row_ptr) != self.n_rows + 1:
            raise ValueError("linear_csr.row_ptr length must be n_rows + 1")
        if self.row_ptr[0] != 0:
            raise ValueError("linear_csr.row_ptr must start at 0")
        if any(value < 0 for value in self.row_ptr):
            raise ValueError("linear_csr.row_ptr values must be nonnegative")
        if any(a > b for a, b in zip(self.row_ptr, self.row_ptr[1:])):
            raise ValueError("linear_csr.row_ptr must be nondecreasing")
        if self.row_ptr[-1] != len(self.col_idx):
            raise ValueError("linear_csr.row_ptr[-1] must equal len(col_idx)")
        if len(self.col_idx) != len(self.coeff):
            raise ValueError("linear_csr.col_idx and coeff lengths must match")
        if len(self.rhs) != self.n_rows:
            raise ValueError("linear_csr.rhs length must equal n_rows")
        if len(self.sense) != self.n_rows:
            raise ValueError("linear_csr.sense length must equal n_rows")
        if len(self.weight) != self.n_rows:
            raise ValueError("linear_csr.weight length must equal n_rows")
        invalid = [value for value in self.sense if value not in SUPPORTED_ROW_SENSES]
        if invalid:
            raise ValueError(f"unsupported row sense values: {invalid}")
        if any(value < 0.0 for value in self.weight):
            raise ValueError("linear_csr.weight values must be nonnegative")

    @property
    def nnz(self) -> int:
        return len(self.col_idx)


@dataclass(frozen=True)
class ProblemSpec:
    """First-stage native problem spec."""

    domain: BinaryDomainSpec
    objective: ObjectiveSpec
    linear_csr: LinearCSRSpec

    def __post_init__(self) -> None:
        n_vars = self.domain.n_vars
        if len(self.objective.linear) != n_vars:
            raise ValueError("objective.linear length must equal domain.n_vars")
        bad_cols = [col for col in self.linear_csr.col_idx if col < 0 or col >= n_vars]
        if bad_cols:
            raise ValueError(f"linear_csr.col_idx values out of range: {bad_cols}")
