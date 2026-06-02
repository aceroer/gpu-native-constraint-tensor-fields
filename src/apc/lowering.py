"""Lower user-facing problem specs into execution-facing CTIR."""

from __future__ import annotations

from .ctir import (
    CTIRProblem,
    LedgerSpec,
    LinearCSR,
    MoveBatch,
    ObjectiveLinear,
    ProjectionSpec,
    VarDomain,
)
from .spec import ProblemSpec


def lower_problem_to_ctir(
    problem: ProblemSpec,
    *,
    batch_size: int = 4,
    moves_per_state: int | None = None,
) -> CTIRProblem:
    """Lower a Phase 1 binary MILP spec into CTIR."""

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    moves = moves_per_state if moves_per_state is not None else problem.domain.n_vars
    linear = problem.linear_csr

    return CTIRProblem(
        domain=VarDomain(
            n_vars=problem.domain.n_vars,
            var_type=tuple("binary" for _ in range(problem.domain.n_vars)),
        ),
        objective=ObjectiveLinear(coeff=problem.objective.linear),
        linear_csr=LinearCSR(
            n_rows=linear.n_rows,
            n_vars=problem.domain.n_vars,
            row_ptr=linear.row_ptr,
            col_idx=linear.col_idx,
            coeff=linear.coeff,
            rhs=linear.rhs,
            sense=linear.sense,
            weight=linear.weight,
        ),
        clause_csr=None,
        qubo_coo=None,
        projection=ProjectionSpec(rules=("binary",)),
        moves=MoveBatch(
            batch_size=batch_size,
            moves_per_state=moves,
            move_type="bit_flip",
            move_dim=1,
        ),
        ledger=LedgerSpec(
            fields=(
                "objective",
                "penalty",
                "feasible_count",
                "active_violation_count",
            )
        ),
    )

