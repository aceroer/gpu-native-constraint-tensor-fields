import json
import tempfile
import unittest
from pathlib import Path

from apc import (
    StateBatch,
    evaluate_maxsat_state,
    load_maxsat_json,
    lower_maxsat_to_ctir,
    run_maxsat_bitflip_repair,
    run_maxsat_runtime_route_from_json,
)


ROOT = Path(__file__).resolve().parents[1]
TINY_MAXSAT = ROOT / "examples" / "specs" / "maxsat_tiny.json"


class MaxSATRuntimeRouteTests(unittest.TestCase):
    def test_route_lowers_through_public_runtime_contract(self):
        report = run_maxsat_runtime_route_from_json(TINY_MAXSAT, batch_size=4, max_iters=4, seed=3)

        self.assertEqual(report["schema"], "apc.maxsat_runtime_route.v1")
        self.assertEqual(report["status"], "implemented")
        self.assertEqual(report["problem_family"], "maxsat")
        self.assertEqual(report["backend"], "cpu")
        self.assertEqual(report["runtime_contract_schema"], "apc.runtime_execution_contract.v1")
        self.assertEqual(report["ctir"]["n_vars"], 3)
        self.assertEqual(report["ctir"]["n_clauses"], 3)
        self.assertEqual(report["ctir"]["clause_nnz"], 6)

    def test_soft_clause_objective_contributions_are_explicit(self):
        spec = load_maxsat_json(TINY_MAXSAT)
        evaluation = evaluate_maxsat_state(spec, (0, 1, 1))

        self.assertEqual(evaluation["objective"], 1.5)
        self.assertEqual(evaluation["penalty"], 0.0)
        self.assertEqual(len(evaluation["soft_objective_contributions"]), 2)
        self.assertEqual(
            evaluation["soft_objective_contributions"][1]["objective_contribution"],
            1.5,
        )

    def test_hard_clause_penalty_contributions_are_explicit(self):
        spec = load_maxsat_json(TINY_MAXSAT)
        evaluation = evaluate_maxsat_state(spec, (0, 0, 0))

        self.assertEqual(evaluation["objective"], 0.0)
        self.assertEqual(evaluation["penalty"], 1.0)
        self.assertEqual(len(evaluation["hard_penalty_contributions"]), 1)
        self.assertEqual(
            evaluation["hard_penalty_contributions"][0]["penalty_contribution"],
            1.0,
        )

    def test_cpu_reference_path_remains_behavioral_baseline(self):
        spec = load_maxsat_json(TINY_MAXSAT)
        problem = lower_maxsat_to_ctir(spec, batch_size=4)
        initial = StateBatch(((0, 0, 0), (1, 1, 1), (1, 0, 0), (0, 1, 0)))
        baseline = run_maxsat_bitflip_repair(problem, max_iters=4, seed=3, initial_states=initial)
        report = run_maxsat_runtime_route_from_json(
            TINY_MAXSAT,
            batch_size=4,
            max_iters=4,
            seed=3,
            initial_states=initial,
        )

        self.assertEqual(report["result"]["best_state"], list(baseline.best_state))
        self.assertEqual(report["result"]["best_penalty"], baseline.best_penalty)
        self.assertEqual(report["result"]["unsatisfied"], list(baseline.unsatisfied))

    def test_unsupported_features_fail_with_structured_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text(
                json.dumps(
                    {
                        "problem_type": "weighted_maxsat",
                        "domain": {"type": "binary", "n_vars": 1},
                        "clauses": [{"lits": [1], "weight": 1.0, "kind": "soft"}],
                        "cardinality": {"at_most_one": [[1]]},
                    }
                ),
                encoding="utf-8",
            )

            report = run_maxsat_runtime_route_from_json(path)

        self.assertEqual(report["schema"], "apc.maxsat_runtime_route.v1")
        self.assertEqual(report["status"], "failed")
        self.assertIn("unsupported MaxSAT fields", report["reason"])
        self.assertEqual(report["problem_family"], "maxsat")


if __name__ == "__main__":
    unittest.main()
