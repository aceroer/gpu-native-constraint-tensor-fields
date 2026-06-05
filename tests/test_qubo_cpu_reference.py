import json
import tempfile
import unittest
from pathlib import Path

from apc import (
    QUBORuntimeConfig,
    StateBatch,
    describe_qubo_cpu_reference_execution_from_json,
    eval_qubo_energy,
    load_qubo_json,
    lower_qubo_to_ctir,
    qubo_ledger_to_dicts,
    run_qubo_cpu_reference,
    run_qubo_cpu_reference_from_json,
)


ROOT = Path(__file__).resolve().parents[1]
TINY_QUBO = ROOT / "examples" / "specs" / "qubo_tiny.json"


class QUBOCPUReferenceTests(unittest.TestCase):
    def test_eval_qubo_energy_matches_tiny_fixture(self):
        problem = lower_qubo_to_ctir(load_qubo_json(TINY_QUBO), batch_size=4)
        states = StateBatch(((0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)))

        self.assertEqual(eval_qubo_energy(problem, states), (0.0, -2.0, -2.25, 0.0))

    def test_qubo_cpu_reference_runs_from_json(self):
        result = run_qubo_cpu_reference_from_json(
            TINY_QUBO,
            config=QUBORuntimeConfig(max_iters=4, batch_size=4, seed=2),
        )

        self.assertEqual(result.best_state, (0, 1, 1))
        self.assertEqual(result.best_objective, -2.25)
        self.assertEqual(result.best_penalty, 0.0)
        self.assertEqual(result.best_energy, -2.25)
        self.assertGreaterEqual(result.move_count, 1)
        self.assertEqual(result.ledger[-1].final_state, (0, 1, 1))

    def test_qubo_cpu_reference_is_deterministic_under_fixed_seed(self):
        config = QUBORuntimeConfig(max_iters=5, batch_size=4, seed=7)

        first = run_qubo_cpu_reference_from_json(TINY_QUBO, config=config)
        second = run_qubo_cpu_reference_from_json(TINY_QUBO, config=config)

        self.assertEqual(first.best_state, second.best_state)
        self.assertEqual(qubo_ledger_to_dicts(first.ledger), qubo_ledger_to_dicts(second.ledger))

    def test_report_records_public_ledger_fields(self):
        report = describe_qubo_cpu_reference_execution_from_json(
            TINY_QUBO,
            config=QUBORuntimeConfig(max_iters=4, batch_size=4, seed=2),
        )

        self.assertEqual(report["schema"], "apc.qubo_cpu_reference_execution.v1")
        self.assertEqual(report["status"], "implemented")
        self.assertEqual(report["execution_status"], "implemented")
        self.assertEqual(report["backend"], "cpu")
        self.assertEqual(report["problem_family"], "qubo")
        self.assertEqual(report["best"]["state"], [0, 1, 1])
        self.assertEqual(report["best"]["energy"], -2.25)
        self.assertIn("energy", report["ledger_fields"])
        self.assertIn("move_count", report["ledger_fields"])
        self.assertIn("final_state", report["ledger_fields"])
        self.assertEqual(report["ledger"][-1]["final_state"], [0, 1, 1])

    def test_unsupported_qubo_inputs_fail_before_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text(
                json.dumps(
                    {
                        "problem_type": "qubo",
                        "domain": {"type": "binary", "n_vars": 2},
                        "objective": {
                            "linear": [0.0, 1.0],
                            "quadratic": [{"i": 0, "j": 2, "weight": 1.0}],
                        },
                    }
                ),
                encoding="utf-8",
            )

            report = describe_qubo_cpu_reference_execution_from_json(path)

        self.assertEqual(report["schema"], "apc.qubo_cpu_reference_execution.v1")
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["backend"], "cpu")
        self.assertIn("out of range", report["reason"])

    def test_runtime_accepts_lowered_qubo_ctir(self):
        problem = lower_qubo_to_ctir(load_qubo_json(TINY_QUBO), batch_size=4)
        result = run_qubo_cpu_reference(problem, config=QUBORuntimeConfig(max_iters=1, batch_size=4))

        self.assertEqual(result.best_penalty, 0.0)


if __name__ == "__main__":
    unittest.main()
