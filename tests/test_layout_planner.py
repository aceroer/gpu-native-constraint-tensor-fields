import json
import subprocess
import sys
import unittest
from pathlib import Path

from apc import (
    layout_summary,
    load_problem_json,
    lower_problem_to_ctir,
    plan_layout,
)
from apc.ctir import (
    CTIRProblem,
    ClauseCSR,
    LedgerSpec,
    MoveBatch,
    ObjectiveLinear,
    ProjectionSpec,
    QUBOCOO,
    VarDomain,
)


ROOT = Path(__file__).resolve().parents[1]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"


class LayoutPlannerTests(unittest.TestCase):
    def test_planner_declares_required_views(self):
        ctir = lower_problem_to_ctir(load_problem_json(TINY_SPEC), batch_size=4)
        plan = plan_layout(ctir)
        views = {view.name: view for view in plan.views}

        self.assertEqual(views["state.candidate_major"].shape, (4, 3))
        self.assertEqual(views["state.variable_major"].shape, (3, 4))
        self.assertFalse(views["state.variable_major"].materialized)
        self.assertEqual(views["linear.csr"].shape, (3, 3, 6))
        self.assertEqual(views["linear.csc"].source, "linear.csr")
        self.assertFalse(views["linear.csc"].materialized)
        self.assertIn("violation.active_compact", views)

    def test_each_runtime_operator_declares_layouts(self):
        ctir = lower_problem_to_ctir(load_problem_json(TINY_SPEC), batch_size=4)
        operators = {operator.operator: operator for operator in plan_layout(ctir).operators}

        expected = {
            "eval_constraints",
            "rectify_violations",
            "reduce_penalty",
            "generate_moves",
            "score_moves",
            "select_moves",
            "apply_moves",
            "apply_projection",
            "reduce_best",
            "record_metrics",
        }
        self.assertEqual(set(operators), expected)
        for operator in operators.values():
            self.assertTrue(operator.inputs, operator.operator)
            self.assertTrue(operator.outputs, operator.operator)

    def test_conversion_costs_are_recorded(self):
        ctir = lower_problem_to_ctir(load_problem_json(TINY_SPEC), batch_size=4)
        costs = {(cost.source, cost.target): cost for cost in plan_layout(ctir).costs}

        state_cost = costs[("state.candidate_major", "state.variable_major")]
        self.assertEqual(state_cost.elements_read, 12)
        self.assertEqual(state_cost.elements_written, 12)

        sparse_cost = costs[("linear.csr", "linear.csc")]
        self.assertEqual(sparse_cost.elements_read, 6)
        self.assertEqual(sparse_cost.elements_written, 6)

        active_cost = costs[("violation.dense", "violation.active_compact")]
        self.assertEqual(active_cost.elements_read, 12)

    def test_layout_summary_is_json_ready(self):
        ctir = lower_problem_to_ctir(load_problem_json(TINY_SPEC), batch_size=2)
        encoded = json.dumps(layout_summary(plan_layout(ctir)), sort_keys=True)
        payload = json.loads(encoded)

        self.assertIn("views", payload)
        self.assertIn("operators", payload)
        self.assertIn("costs", payload)
        self.assertEqual(payload["views"][0]["name"], "state.candidate_major")

    def test_placeholder_problem_views_are_explicit(self):
        problem = CTIRProblem(
            domain=VarDomain(n_vars=2, var_type=("binary", "binary")),
            objective=ObjectiveLinear(coeff=(1.0, 2.0)),
            linear_csr=None,
            clause_csr=ClauseCSR(
                n_clauses=1,
                clause_ptr=(0, 2),
                lit_var=(0, 1),
                lit_sign=(1, -1),
                weight=(1.0,),
            ),
            qubo_coo=QUBOCOO(n_vars=2, i=(0,), j=(1,), q=(0.5,)),
            projection=ProjectionSpec(rules=("binary",)),
            moves=MoveBatch(batch_size=3, moves_per_state=2, move_type="bit_flip", move_dim=1),
            ledger=LedgerSpec(fields=("objective", "penalty")),
        )

        summary = layout_summary(plan_layout(problem))
        views = {view["name"]: view for view in summary["views"]}
        score = [operator for operator in summary["operators"] if operator["operator"] == "score_moves"][0]

        self.assertIn("clause.csr", views)
        self.assertIn("qubo.coo", views)
        self.assertIn("clause.csr", score["inputs"])
        self.assertIn("qubo.coo", score["inputs"])

    def test_cli_prints_layout_summary(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "apc.cli",
                "layout",
                str(TINY_SPEC),
                "--batch-size",
                "5",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        views = {view["name"]: view for view in payload["views"]}
        self.assertEqual(views["state.candidate_major"]["shape"], [5, 3])
        self.assertTrue(payload["costs"])


if __name__ == "__main__":
    unittest.main()
