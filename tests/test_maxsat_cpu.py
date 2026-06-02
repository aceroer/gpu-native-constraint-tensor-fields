import unittest
from pathlib import Path

from apc import (
    StateBatch,
    ctir_to_dict,
    eval_unsatisfied_clauses,
    layout_summary,
    load_maxsat_json,
    lower_maxsat_to_ctir,
    maxsat_penalty,
    plan_layout,
    run_maxsat_bitflip_repair,
)


ROOT = Path(__file__).resolve().parents[1]
TINY_MAXSAT = ROOT / "examples" / "specs" / "maxsat_tiny.json"


class MaxSATCPUTests(unittest.TestCase):
    def test_load_tiny_weighted_maxsat(self):
        spec = load_maxsat_json(TINY_MAXSAT)

        self.assertEqual(spec.n_vars, 3)
        self.assertEqual(len(spec.clauses), 3)
        self.assertEqual(spec.clauses[0].literals, (1, 2))
        self.assertEqual(spec.clauses[1].weight, 2.0)

    def test_lower_maxsat_to_clause_csr_ctir(self):
        problem = lower_maxsat_to_ctir(load_maxsat_json(TINY_MAXSAT), batch_size=4)
        encoded = ctir_to_dict(problem)

        self.assertIsNotNone(problem.clause_csr)
        self.assertEqual(problem.clause_csr.n_clauses, 3)
        self.assertEqual(problem.clause_csr.clause_ptr, (0, 2, 4, 6))
        self.assertEqual(problem.clause_csr.lit_var, (0, 1, 0, 2, 1, 2))
        self.assertEqual(problem.clause_csr.lit_sign, (1, 1, -1, 1, -1, -1))
        self.assertEqual(encoded["clause_csr"]["nnz"], 6)

    def test_evaluate_unsatisfied_clause_indicators(self):
        problem = lower_maxsat_to_ctir(load_maxsat_json(TINY_MAXSAT), batch_size=3)
        states = StateBatch(((0, 0, 0), (1, 0, 1), (0, 1, 1)))

        unsatisfied = eval_unsatisfied_clauses(problem.clause_csr, states)
        penalties = maxsat_penalty(problem.clause_csr, unsatisfied)

        self.assertEqual(unsatisfied, ((1, 0, 0), (0, 0, 0), (0, 0, 1)))
        self.assertEqual(penalties, (1.0, 0.0, 1.5))

    def test_run_bitflip_repair_on_cpu(self):
        problem = lower_maxsat_to_ctir(load_maxsat_json(TINY_MAXSAT), batch_size=4)
        initial = StateBatch(((0, 0, 0), (1, 1, 1), (1, 0, 0), (0, 1, 0)))
        result = run_maxsat_bitflip_repair(problem, max_iters=4, seed=3, initial_states=initial)

        self.assertEqual(result.best_penalty, 0.0)
        self.assertEqual(result.unsatisfied, (0, 0, 0))
        self.assertTrue(all(value in (0, 1) for value in result.best_state))

    def test_layout_exposes_clause_view(self):
        problem = lower_maxsat_to_ctir(load_maxsat_json(TINY_MAXSAT), batch_size=4)
        summary = layout_summary(plan_layout(problem))
        views = {view["name"]: view for view in summary["views"]}

        self.assertIn("clause.csr", views)
        self.assertEqual(views["clause.csr"]["shape"], [3, 6])


if __name__ == "__main__":
    unittest.main()
