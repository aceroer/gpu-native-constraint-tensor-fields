"""Device layout planning for CTIR problems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ctir import CTIRProblem
from .layout_ledger import LayoutCost, layout_costs_to_dicts


CANDIDATE_MAJOR = "state.candidate_major"
VARIABLE_MAJOR = "state.variable_major"
LINEAR_CSR = "linear.csr"
LINEAR_CSC = "linear.csc"
CLAUSE_CSR = "clause.csr"
QUBO_COO = "qubo.coo"
VIOLATION_DENSE = "violation.dense"
VIOLATION_ACTIVE = "violation.active_compact"
MOVE_BIT_FLIP = "move.bit_flip"
LEDGER_DENSE = "ledger.dense"


@dataclass(frozen=True)
class LayoutView:
    """One explicit tensor layout view."""

    name: str
    shape: tuple[int, ...]
    dtype: str
    source: str
    materialized: bool = True


@dataclass(frozen=True)
class OperatorLayout:
    """Required input and output layouts for one operator."""

    operator: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


@dataclass(frozen=True)
class LayoutPlan:
    """A CTIR device layout plan."""

    views: tuple[LayoutView, ...]
    operators: tuple[OperatorLayout, ...]
    costs: tuple[LayoutCost, ...]


def plan_layout(problem: CTIRProblem) -> LayoutPlan:
    """Plan explicit device layouts for the currently supported CTIR surface."""

    views: list[LayoutView] = [
        LayoutView(
            name=CANDIDATE_MAJOR,
            shape=(problem.moves.batch_size, problem.domain.n_vars),
            dtype="int32",
            source="state_batch",
        ),
        LayoutView(
            name=VARIABLE_MAJOR,
            shape=(problem.domain.n_vars, problem.moves.batch_size),
            dtype="int32",
            source=CANDIDATE_MAJOR,
            materialized=False,
        ),
        LayoutView(
            name=VIOLATION_DENSE,
            shape=(problem.moves.batch_size, _constraint_count(problem)),
            dtype="float64",
            source="operator_output",
        ),
        LayoutView(
            name=VIOLATION_ACTIVE,
            shape=(problem.moves.batch_size, _constraint_count(problem)),
            dtype="int32",
            source=VIOLATION_DENSE,
            materialized=False,
        ),
        LayoutView(
            name=MOVE_BIT_FLIP,
            shape=(problem.moves.batch_size, problem.moves.moves_per_state, problem.moves.move_dim),
            dtype="int32",
            source="move_generator",
        ),
        LayoutView(
            name=LEDGER_DENSE,
            shape=(problem.moves.batch_size,),
            dtype="float64",
            source="reduction_output",
        ),
    ]

    if problem.linear_csr is not None:
        linear = problem.linear_csr
        views.extend(
            [
                LayoutView(
                    name=LINEAR_CSR,
                    shape=(linear.n_rows, linear.n_vars, linear.nnz),
                    dtype="mixed",
                    source="ctir.linear_csr",
                ),
                LayoutView(
                    name=LINEAR_CSC,
                    shape=(linear.n_vars, linear.n_rows, linear.nnz),
                    dtype="mixed",
                    source=LINEAR_CSR,
                    materialized=False,
                ),
            ]
        )

    if problem.clause_csr is not None:
        views.append(
            LayoutView(
                name=CLAUSE_CSR,
                shape=(problem.clause_csr.n_clauses, len(problem.clause_csr.lit_var)),
                dtype="mixed",
                source="ctir.clause_csr",
            )
        )

    if problem.qubo_coo is not None:
        views.append(
            LayoutView(
                name=QUBO_COO,
                shape=(len(problem.qubo_coo.q),),
                dtype="mixed",
                source="ctir.qubo_coo",
            )
        )

    operators = _operator_layouts(problem)
    costs = _layout_costs(problem)
    return LayoutPlan(views=tuple(views), operators=operators, costs=costs)


def layout_summary(plan: LayoutPlan) -> dict[str, Any]:
    """Return a compact printable layout summary."""

    return {
        "views": [
            {
                "name": view.name,
                "shape": list(view.shape),
                "dtype": view.dtype,
                "source": view.source,
                "materialized": view.materialized,
            }
            for view in plan.views
        ],
        "operators": [
            {
                "operator": operator.operator,
                "inputs": list(operator.inputs),
                "outputs": list(operator.outputs),
            }
            for operator in plan.operators
        ],
        "costs": layout_costs_to_dicts(plan.costs),
    }


def _operator_layouts(problem: CTIRProblem) -> tuple[OperatorLayout, ...]:
    operators: list[OperatorLayout] = []
    if problem.linear_csr is not None:
        operators.extend(
            [
                OperatorLayout(
                    operator="eval_constraints",
                    inputs=(CANDIDATE_MAJOR, LINEAR_CSR),
                    outputs=("constraint.response_dense",),
                ),
                OperatorLayout(
                    operator="rectify_violations",
                    inputs=("constraint.response_dense", LINEAR_CSR),
                    outputs=(VIOLATION_DENSE,),
                ),
                OperatorLayout(
                    operator="reduce_penalty",
                    inputs=(VIOLATION_DENSE, LINEAR_CSR),
                    outputs=(LEDGER_DENSE,),
                ),
            ]
        )
    operators.extend(
        [
            OperatorLayout(
                operator="generate_moves",
                inputs=(CANDIDATE_MAJOR,),
                outputs=(MOVE_BIT_FLIP,),
            ),
            OperatorLayout(
                operator="score_moves",
                inputs=(CANDIDATE_MAJOR, MOVE_BIT_FLIP, *_interaction_views(problem)),
                outputs=("move.score_dense",),
            ),
            OperatorLayout(
                operator="select_moves",
                inputs=("move.score_dense",),
                outputs=("move.selected",),
            ),
            OperatorLayout(
                operator="apply_moves",
                inputs=(CANDIDATE_MAJOR, "move.selected"),
                outputs=(CANDIDATE_MAJOR,),
            ),
            OperatorLayout(
                operator="apply_projection",
                inputs=(CANDIDATE_MAJOR,),
                outputs=(CANDIDATE_MAJOR,),
            ),
            OperatorLayout(
                operator="reduce_best",
                inputs=(CANDIDATE_MAJOR, LEDGER_DENSE),
                outputs=("best.candidate",),
            ),
            OperatorLayout(
                operator="record_metrics",
                inputs=(LEDGER_DENSE, VIOLATION_ACTIVE),
                outputs=("validation.ledger",),
            ),
        ]
    )
    return tuple(operators)


def _layout_costs(problem: CTIRProblem) -> tuple[LayoutCost, ...]:
    costs: list[LayoutCost] = []
    state_elements = problem.moves.batch_size * problem.domain.n_vars
    costs.append(
        LayoutCost(
            source=CANDIDATE_MAJOR,
            target=VARIABLE_MAJOR,
            elements_read=state_elements,
            elements_written=state_elements,
            reason="dual state view for variable-major access",
        )
    )
    constraint_elements = problem.moves.batch_size * _constraint_count(problem)
    costs.append(
        LayoutCost(
            source=VIOLATION_DENSE,
            target=VIOLATION_ACTIVE,
            elements_read=constraint_elements,
            elements_written=constraint_elements,
            reason="active violation compaction upper bound",
        )
    )
    if problem.linear_csr is not None:
        linear = problem.linear_csr
        costs.append(
            LayoutCost(
                source=LINEAR_CSR,
                target=LINEAR_CSC,
                elements_read=linear.nnz,
                elements_written=linear.nnz,
                reason="dual sparse view for variable incidence",
            )
        )
    return tuple(costs)


def _interaction_views(problem: CTIRProblem) -> tuple[str, ...]:
    views: list[str] = []
    if problem.linear_csr is not None:
        views.extend([LINEAR_CSR, LINEAR_CSC])
    if problem.clause_csr is not None:
        views.append(CLAUSE_CSR)
    if problem.qubo_coo is not None:
        views.append(QUBO_COO)
    return tuple(views)


def _constraint_count(problem: CTIRProblem) -> int:
    count = 0
    if problem.linear_csr is not None:
        count += problem.linear_csr.n_rows
    if problem.clause_csr is not None:
        count += problem.clause_csr.n_clauses
    return count
