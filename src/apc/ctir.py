"""Execution-facing Constraint Tensor IR objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SUPPORTED_DOMAIN_TYPES = ("binary",)
SUPPORTED_PROJECTION_RULES = ("binary",)
SUPPORTED_MOVE_TYPES = ("bit_flip",)
SUPPORTED_LEDGER_FIELDS = (
    "objective",
    "penalty",
    "feasible_count",
    "active_violation_count",
)


@dataclass(frozen=True)
class VarDomain:
    """Execution-facing variable-domain metadata."""

    n_vars: int
    var_type: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.n_vars <= 0:
            raise ValueError("VarDomain.n_vars must be positive")
        if len(self.var_type) != self.n_vars:
            raise ValueError("VarDomain.var_type length must equal n_vars")
        invalid = [value for value in self.var_type if value not in SUPPORTED_DOMAIN_TYPES]
        if invalid:
            raise ValueError(f"unsupported domain types: {invalid}")


@dataclass(frozen=True)
class LinearCSR:
    """Execution-facing sparse linear constraints."""

    n_rows: int
    n_vars: int
    row_ptr: tuple[int, ...]
    col_idx: tuple[int, ...]
    coeff: tuple[float, ...]
    rhs: tuple[float, ...]
    sense: tuple[str, ...]
    weight: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.n_rows <= 0:
            raise ValueError("LinearCSR.n_rows must be positive")
        if self.n_vars <= 0:
            raise ValueError("LinearCSR.n_vars must be positive")
        if len(self.row_ptr) != self.n_rows + 1:
            raise ValueError("LinearCSR.row_ptr length must be n_rows + 1")
        if self.row_ptr[0] != 0:
            raise ValueError("LinearCSR.row_ptr must start at 0")
        if any(value < 0 for value in self.row_ptr):
            raise ValueError("LinearCSR.row_ptr values must be nonnegative")
        if any(a > b for a, b in zip(self.row_ptr, self.row_ptr[1:])):
            raise ValueError("LinearCSR.row_ptr must be nondecreasing")
        if self.row_ptr[-1] != len(self.col_idx):
            raise ValueError("LinearCSR.row_ptr[-1] must equal len(col_idx)")
        if len(self.col_idx) != len(self.coeff):
            raise ValueError("LinearCSR.col_idx and coeff lengths must match")
        if len(self.rhs) != self.n_rows:
            raise ValueError("LinearCSR.rhs length must equal n_rows")
        if len(self.sense) != self.n_rows:
            raise ValueError("LinearCSR.sense length must equal n_rows")
        if len(self.weight) != self.n_rows:
            raise ValueError("LinearCSR.weight length must equal n_rows")
        bad_cols = [col for col in self.col_idx if col < 0 or col >= self.n_vars]
        if bad_cols:
            raise ValueError(f"LinearCSR.col_idx values out of range: {bad_cols}")

    @property
    def nnz(self) -> int:
        return len(self.col_idx)


@dataclass(frozen=True)
class ClauseCSR:
    """Placeholder for SAT / MaxSAT clause constraints."""

    n_clauses: int = 0
    clause_ptr: tuple[int, ...] = (0,)
    lit_var: tuple[int, ...] = ()
    lit_sign: tuple[int, ...] = ()
    weight: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if self.n_clauses < 0:
            raise ValueError("ClauseCSR.n_clauses must be nonnegative")
        if len(self.clause_ptr) != self.n_clauses + 1:
            raise ValueError("ClauseCSR.clause_ptr length must be n_clauses + 1")
        if self.clause_ptr[0] != 0:
            raise ValueError("ClauseCSR.clause_ptr must start at 0")
        if any(value < 0 for value in self.clause_ptr):
            raise ValueError("ClauseCSR.clause_ptr values must be nonnegative")
        if any(a > b for a, b in zip(self.clause_ptr, self.clause_ptr[1:])):
            raise ValueError("ClauseCSR.clause_ptr must be nondecreasing")
        if self.clause_ptr[-1] != len(self.lit_var):
            raise ValueError("ClauseCSR.clause_ptr[-1] must equal len(lit_var)")
        if len(self.lit_var) != len(self.lit_sign):
            raise ValueError("ClauseCSR.lit_var and lit_sign lengths must match")
        if len(self.weight) != self.n_clauses:
            raise ValueError("ClauseCSR.weight length must equal n_clauses")
        invalid_signs = [value for value in self.lit_sign if value not in (-1, 1)]
        if invalid_signs:
            raise ValueError(f"ClauseCSR.lit_sign values must be -1 or 1: {invalid_signs}")
        if any(value < 0.0 for value in self.weight):
            raise ValueError("ClauseCSR.weight values must be nonnegative")

    @property
    def nnz(self) -> int:
        return len(self.lit_var)


@dataclass(frozen=True)
class QUBOCOO:
    """Placeholder for QUBO graph-energy constraints."""

    n_vars: int = 0
    i: tuple[int, ...] = ()
    j: tuple[int, ...] = ()
    q: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if self.n_vars <= 0:
            raise ValueError("QUBOCOO.n_vars must be positive")
        if len(self.i) != len(self.j) or len(self.i) != len(self.q):
            raise ValueError("QUBOCOO i, j, and q lengths must match")
        bad_i = [value for value in self.i if value < 0 or value >= self.n_vars]
        bad_j = [value for value in self.j if value < 0 or value >= self.n_vars]
        if bad_i or bad_j:
            raise ValueError(f"QUBOCOO indices out of range: i={bad_i}, j={bad_j}")


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
class ViolationBatch:
    """Shape-only violation batch metadata."""

    batch_size: int
    n_constraints: int
    compressed: bool = False


@dataclass(frozen=True)
class MoveBatch:
    """Shape-only move batch metadata."""

    batch_size: int
    moves_per_state: int
    move_type: str
    move_dim: int

    def __post_init__(self) -> None:
        if self.move_type not in SUPPORTED_MOVE_TYPES:
            raise ValueError(f"unsupported move type: {self.move_type}")
        if self.batch_size <= 0:
            raise ValueError("MoveBatch.batch_size must be positive")
        if self.moves_per_state <= 0:
            raise ValueError("MoveBatch.moves_per_state must be positive")
        if self.move_dim <= 0:
            raise ValueError("MoveBatch.move_dim must be positive")


@dataclass(frozen=True)
class ProjectionSpec:
    """Domain projection rules."""

    rules: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.rules) == 0:
            raise ValueError("ProjectionSpec.rules must not be empty")
        invalid = [rule for rule in self.rules if rule not in SUPPORTED_PROJECTION_RULES]
        if invalid:
            raise ValueError(f"unsupported projection rules: {invalid}")


@dataclass(frozen=True)
class LedgerSpec:
    """Metrics expected from a runtime."""

    fields: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.fields) == 0:
            raise ValueError("LedgerSpec.fields must not be empty")
        invalid = [field for field in self.fields if field not in SUPPORTED_LEDGER_FIELDS]
        if invalid:
            raise ValueError(f"unsupported ledger fields: {invalid}")


@dataclass(frozen=True)
class ObjectiveLinear:
    """Execution-facing linear objective."""

    coeff: tuple[float, ...]


@dataclass(frozen=True)
class CTIRProblem:
    """Execution-facing problem representation."""

    domain: VarDomain
    objective: ObjectiveLinear
    linear_csr: LinearCSR | None
    clause_csr: ClauseCSR | None
    qubo_coo: QUBOCOO | None
    projection: ProjectionSpec
    moves: MoveBatch
    ledger: LedgerSpec

    def __post_init__(self) -> None:
        n_vars = self.domain.n_vars
        if len(self.objective.coeff) != n_vars:
            raise ValueError("ObjectiveLinear.coeff length must equal domain.n_vars")
        if self.linear_csr is None and self.clause_csr is None and self.qubo_coo is None:
            raise ValueError("CTIRProblem must include at least one constraint or energy view")
        if self.linear_csr is not None and self.linear_csr.n_vars != n_vars:
            raise ValueError("LinearCSR.n_vars must match domain.n_vars")
        if self.qubo_coo is not None and self.qubo_coo.n_vars != n_vars:
            raise ValueError("QUBOCOO.n_vars must match domain.n_vars")


def ctir_to_dict(problem: CTIRProblem) -> dict[str, Any]:
    """Serialize CTIR into an inspectable dictionary."""

    return {
        "domain": {
            "n_vars": problem.domain.n_vars,
            "var_type": list(problem.domain.var_type),
        },
        "objective": {
            "linear": list(problem.objective.coeff),
        },
        "linear_csr": _linear_to_dict(problem.linear_csr),
        "clause_csr": _clause_to_dict(problem.clause_csr),
        "qubo_coo": _qubo_to_dict(problem.qubo_coo),
        "projection": {
            "rules": list(problem.projection.rules),
        },
        "moves": {
            "batch_size": problem.moves.batch_size,
            "moves_per_state": problem.moves.moves_per_state,
            "move_type": problem.moves.move_type,
            "move_dim": problem.moves.move_dim,
        },
        "ledger": {
            "fields": list(problem.ledger.fields),
        },
    }


def _linear_to_dict(linear: LinearCSR | None) -> dict[str, Any] | None:
    if linear is None:
        return None
    return {
        "n_rows": linear.n_rows,
        "n_vars": linear.n_vars,
        "nnz": linear.nnz,
        "row_ptr": list(linear.row_ptr),
        "col_idx": list(linear.col_idx),
        "coeff": list(linear.coeff),
        "rhs": list(linear.rhs),
        "sense": list(linear.sense),
        "weight": list(linear.weight),
    }


def _clause_to_dict(clause: ClauseCSR | None) -> dict[str, Any] | None:
    if clause is None:
        return None
    return {
        "n_clauses": clause.n_clauses,
        "nnz": clause.nnz,
        "clause_ptr": list(clause.clause_ptr),
        "lit_var": list(clause.lit_var),
        "lit_sign": list(clause.lit_sign),
        "weight": list(clause.weight),
    }


def _qubo_to_dict(qubo: QUBOCOO | None) -> dict[str, Any] | None:
    if qubo is None:
        return None
    return {
        "n_vars": qubo.n_vars,
        "nnz": len(qubo.q),
        "i": list(qubo.i),
        "j": list(qubo.j),
        "q": list(qubo.q),
    }
