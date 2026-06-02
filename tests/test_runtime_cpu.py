import unittest
from pathlib import Path

from apc import (
    RuntimeConfig,
    StateBatch,
    ledger_to_dicts,
    load_problem_json,
    lower_problem_to_ctir,
    run_repair,
    run_repair_from_json,
)
from apc.operators_cpu import (
    apply_projection,
    eval_constraints,
    generate_moves,
    objective_values,
    rectify_violations,
    reduce_penalty,
)


ROOT = Path(__file__).resolve().parents[1]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"


class CPURuntimeTests(unittest.TestCase):
    def test_operator_chain_evaluates_linear_penalties(self):
        problem = lower_problem_to_ctir(load_problem_json(TINY_SPEC), batch_size=2)
        states = StateBatch(((0, 0, 0), (0, 1, 0)))

        responses = eval_constraints(problem, states)
        violations = rectify_violations(problem, responses)
        penalties = reduce_penalty(problem, violations)
        objectives = objective_values(problem, states)

        self.assertEqual(responses, ((0.0, 0.0, 0.0), (1.0, 1.0, 0.0)))
        self.assertEqual(violations, ((1.0, 1.0, 0.0), (0.0, 0.0, 0.0)))
        self.assertEqual(penalties, (2.0, 0.0))
        self.assertEqual(objectives, (0.0, 1.0))

    def test_run_full_repair_loop_from_json_spec(self):
        initial = StateBatch(((0, 0, 0), (1, 1, 1), (1, 0, 0), (0, 1, 0)))
        result = run_repair_from_json(
            TINY_SPEC,
            config=RuntimeConfig(max_iters=4, batch_size=4, seed=7),
            initial_states=initial,
        )

        self.assertEqual(result.best_state, (0, 1, 0))
        self.assertEqual(result.best_objective, 1.0)
        self.assertEqual(result.best_penalty, 0.0)
        self.assertGreaterEqual(result.ledger[-1].feasible_count, 1)
        self.assertEqual(result.ledger[-1].active_violation_count, 0)

    def test_ledger_records_required_public_fields(self):
        result = run_repair_from_json(
            TINY_SPEC,
            config=RuntimeConfig(max_iters=2, batch_size=4, seed=0),
        )
        rows = ledger_to_dicts(result.ledger)

        self.assertEqual(
            set(rows[0]),
            {"iteration", "objective", "penalty", "feasible_count", "active_violation_count"},
        )
        self.assertEqual(rows[0]["iteration"], 0)
        self.assertIsInstance(rows[-1]["objective"], float)
        self.assertIsInstance(rows[-1]["penalty"], float)
        self.assertIsInstance(rows[-1]["feasible_count"], int)
        self.assertIsInstance(rows[-1]["active_violation_count"], int)

    def test_projection_keeps_binary_domain_invariants(self):
        problem = lower_problem_to_ctir(load_problem_json(TINY_SPEC), batch_size=2)
        projected = apply_projection(problem, StateBatch(((-2, 0, 4), (1, 2, -1))))

        self.assertEqual(projected.x, ((0, 0, 1), (1, 1, 0)))
        for state in projected.x:
            self.assertTrue(all(value in (0, 1) for value in state))

    def test_fixed_seed_is_deterministic(self):
        config = RuntimeConfig(max_iters=5, batch_size=5, seed=13)
        first = run_repair_from_json(TINY_SPEC, config=config)
        second = run_repair_from_json(TINY_SPEC, config=config)

        self.assertEqual(first.best_state, second.best_state)
        self.assertEqual(first.best_objective, second.best_objective)
        self.assertEqual(first.best_penalty, second.best_penalty)
        self.assertEqual(ledger_to_dicts(first.ledger), ledger_to_dicts(second.ledger))

    def test_generated_moves_match_ctir_shape(self):
        problem = lower_problem_to_ctir(load_problem_json(TINY_SPEC), batch_size=3)
        states = StateBatch(((0, 0, 0), (1, 0, 1), (0, 1, 0)))
        moves = generate_moves(problem, states)

        self.assertEqual(len(moves), 3)
        self.assertEqual([len(row) for row in moves], [3, 3, 3])

    def test_run_repair_accepts_lowered_ctir_directly(self):
        problem = lower_problem_to_ctir(load_problem_json(TINY_SPEC), batch_size=4)
        result = run_repair(problem, config=RuntimeConfig(max_iters=3, batch_size=4, seed=3))

        self.assertEqual(result.best_penalty, 0.0)


if __name__ == "__main__":
    unittest.main()
