"""CTIR inspection helpers."""

from __future__ import annotations

import json

from .ctir import CTIRProblem, ctir_to_dict


def inspect_ctir(problem: CTIRProblem) -> dict[str, object]:
    """Return a compact summary suitable for CLI output."""

    linear = problem.linear_csr
    return {
        "domain": {
            "n_vars": problem.domain.n_vars,
            "types": sorted(set(problem.domain.var_type)),
        },
        "objective": {
            "kind": "linear",
            "n_coeff": len(problem.objective.coeff),
        },
        "constraints": {
            "linear_rows": linear.n_rows if linear is not None else 0,
            "linear_nnz": linear.nnz if linear is not None else 0,
            "clauses": problem.clause_csr.n_clauses if problem.clause_csr else 0,
            "qubo_terms": len(problem.qubo_coo.q) if problem.qubo_coo else 0,
        },
        "projection": list(problem.projection.rules),
        "moves": {
            "type": problem.moves.move_type,
            "moves_per_state": problem.moves.moves_per_state,
            "move_dim": problem.moves.move_dim,
        },
        "ledger": list(problem.ledger.fields),
    }


def ctir_json(problem: CTIRProblem, *, indent: int = 2) -> str:
    """Serialize full CTIR to stable JSON."""

    return json.dumps(ctir_to_dict(problem), indent=indent, sort_keys=True)

