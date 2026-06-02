import json
import tempfile
import unittest
from pathlib import Path

from apc import (
    ctir_to_dict,
    describe_qubo_lowering_from_json,
    layout_summary,
    load_qubo_json,
    lower_qubo_to_ctir,
    plan_layout,
)
from apc.ctir import QUBOCOO


ROOT = Path(__file__).resolve().parents[1]
TINY_QUBO = ROOT / "examples" / "specs" / "qubo_tiny.json"


class QUBOSpecLoweringTests(unittest.TestCase):
    def test_qubo_example_validates_as_public_spec(self):
        spec = load_qubo_json(TINY_QUBO)

        self.assertEqual(spec.n_vars, 3)
        self.assertEqual(spec.linear, (1.0, -2.0, 0.5))
        self.assertEqual(len(spec.quadratic), 2)
        self.assertEqual(spec.quadratic[0].i, 0)
        self.assertEqual(spec.quadratic[0].j, 1)
        self.assertEqual(spec.quadratic[0].weight, 1.25)

    def test_qubo_coo_entries_lower_into_ctir_metadata(self):
        problem = lower_qubo_to_ctir(load_qubo_json(TINY_QUBO), batch_size=5)
        payload = ctir_to_dict(problem)

        self.assertIsNotNone(problem.qubo_coo)
        self.assertEqual(problem.qubo_coo.n_vars, 3)
        self.assertEqual(problem.qubo_coo.i, (0, 1))
        self.assertEqual(problem.qubo_coo.j, (1, 2))
        self.assertEqual(problem.qubo_coo.q, (1.25, -0.75))
        self.assertEqual(payload["qubo_coo"]["nnz"], 2)
        self.assertEqual(payload["objective"]["linear"], [1.0, -2.0, 0.5])

    def test_linear_and_quadratic_terms_are_reported_explicitly(self):
        report = describe_qubo_lowering_from_json(TINY_QUBO, batch_size=5)

        self.assertEqual(report["schema"], "apc.qubo_lowering.v1")
        self.assertEqual(report["status"], "implemented")
        self.assertEqual(report["problem_family"], "qubo")
        self.assertEqual(report["execution_status"], "planned")
        self.assertEqual(report["ctir"]["linear_terms"], [1.0, -2.0, 0.5])
        self.assertEqual(
            report["ctir"]["quadratic_terms"],
            [
                {"i": 0, "j": 1, "weight": 1.25},
                {"i": 1, "j": 2, "weight": -0.75},
            ],
        )

    def test_qubo_layout_exposes_energy_view(self):
        problem = lower_qubo_to_ctir(load_qubo_json(TINY_QUBO), batch_size=5)
        summary = layout_summary(plan_layout(problem))
        views = {view["name"]: view for view in summary["views"]}
        score = [operator for operator in summary["operators"] if operator["operator"] == "score_moves"][0]

        self.assertIn("qubo.coo", views)
        self.assertEqual(views["qubo.coo"]["shape"], [2])
        self.assertIn("qubo.coo", score["inputs"])

    def test_qubo_coo_validation_rejects_bad_shapes(self):
        with self.assertRaisesRegex(ValueError, "lengths must match"):
            QUBOCOO(n_vars=2, i=(0,), j=(1, 0), q=(1.0,))
        with self.assertRaisesRegex(ValueError, "out of range"):
            QUBOCOO(n_vars=2, i=(0,), j=(2,), q=(1.0,))

    def test_unsupported_features_fail_with_structured_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text(
                json.dumps(
                    {
                        "problem_type": "qubo",
                        "domain": {"type": "binary", "n_vars": 2},
                        "objective": {
                            "linear": [0.0, 1.0],
                            "quadratic": [{"i": 0, "j": 1, "weight": 2.0}],
                        },
                        "constraints": {"linear": []},
                    }
                ),
                encoding="utf-8",
            )

            report = describe_qubo_lowering_from_json(path)

        self.assertEqual(report["schema"], "apc.qubo_lowering.v1")
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["execution_status"], "planned")
        self.assertIn("unsupported QUBO fields", report["reason"])

    def test_cpu_execution_boundary_remains_explicit(self):
        report = describe_qubo_lowering_from_json(TINY_QUBO)
        text = json.dumps(report).lower()

        self.assertEqual(report["execution_status"], "planned")
        self.assertIn("not implemented in the cpu reference runtime", text)
        self.assertNotIn("compatible with", text)


if __name__ == "__main__":
    unittest.main()
