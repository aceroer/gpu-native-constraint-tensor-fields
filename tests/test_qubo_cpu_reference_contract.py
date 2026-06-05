import json
import tempfile
import unittest
from pathlib import Path

from apc import (
    QUBO_LEDGER_FIELDS,
    default_qubo_cpu_reference_contract,
    describe_qubo_cpu_reference_contract,
    describe_qubo_cpu_reference_contract_from_json,
)


ROOT = Path(__file__).resolve().parents[1]
TINY_QUBO = ROOT / "examples" / "specs" / "qubo_tiny.json"


class QUBOCPUReferenceContractTests(unittest.TestCase):
    def test_contract_names_qubo_runtime_surface(self):
        report = describe_qubo_cpu_reference_contract()

        self.assertEqual(report["schema"], "apc.qubo_cpu_reference_contract.v1")
        self.assertEqual(report["name"], "qubo_cpu_reference_runtime")
        self.assertEqual(report["backend"], "cpu")
        self.assertEqual(report["problem_families"], ["qubo"])
        self.assertEqual(report["execution_status"], "planned")
        self.assertEqual(report["ledger_fields"], list(QUBO_LEDGER_FIELDS))

    def test_contract_names_required_steps(self):
        report = describe_qubo_cpu_reference_contract()
        steps = {step["name"]: step for step in report["steps"]}

        for name in (
            "load_qubo_spec",
            "lower_qubo_to_ctir",
            "initialize_binary_state_pool",
            "evaluate_qubo_energy",
            "generate_bitflip_moves",
            "score_qubo_bitflip_moves",
            "select_reduction_gate_actions",
            "apply_selected_actions",
            "project_binary_domain",
            "record_qubo_ledger",
            "project_public_summary",
        ):
            self.assertIn(name, steps)

        self.assertEqual(steps["evaluate_qubo_energy"]["operator_name"], "eval_qubo_energy")
        self.assertEqual(
            steps["score_qubo_bitflip_moves"]["operator_name"],
            "score_qubo_bitflip_moves",
        )
        self.assertEqual(steps["record_qubo_ledger"]["kind"], "ledger")

    def test_contract_gates_cuda_on_cpu_reference(self):
        report = describe_qubo_cpu_reference_contract()
        text = json.dumps(report).lower()

        self.assertIn("deterministic cpu behavior", text)
        self.assertIn("cuda parity is gated", text)
        self.assertIn("complete timing evidence", text)
        self.assertNotIn("compatible with", text)
        self.assertNotIn("speedup", text)

    def test_contract_report_from_json_names_ctir_and_call_ledger_shape(self):
        report = describe_qubo_cpu_reference_contract_from_json(TINY_QUBO, batch_size=5)

        self.assertEqual(report["status"], "implemented")
        self.assertEqual(report["execution_status"], "planned")
        self.assertEqual(report["source_path"], str(TINY_QUBO))
        self.assertEqual(report["config"]["batch_size"], 5)
        self.assertEqual(report["config"]["moves_per_state"], 3)
        self.assertEqual(report["ctir"]["n_vars"], 3)
        self.assertEqual(report["ctir"]["qubo_nnz"], 2)
        self.assertEqual(report["call_ledger_shape"]["schema"], "apc.operator_call_ledger.v1")
        self.assertIn(
            "record_qubo_ledger",
            [row["step_name"] for row in report["call_ledger_shape"]["rows"]],
        )

    def test_contract_rejects_unsupported_inputs_before_execution(self):
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

            report = describe_qubo_cpu_reference_contract_from_json(path)

        self.assertEqual(report["schema"], "apc.qubo_cpu_reference_contract.v1")
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["execution_status"], "planned")
        self.assertIn("out of range", report["reason"])

    def test_dataclass_contract_is_json_ready(self):
        contract = default_qubo_cpu_reference_contract()

        self.assertEqual(contract.version, "apc.qubo_cpu_reference_contract.v1")
        self.assertEqual(contract.problem_families, ("qubo",))
        self.assertGreater(len(contract.steps), 0)


if __name__ == "__main__":
    unittest.main()
