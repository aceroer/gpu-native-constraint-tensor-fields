import json
import unittest
from pathlib import Path

from apc.io_json import load_problem_json
from apc.lowering import lower_problem_to_ctir
from apc.operator_call_ledger import (
    OperatorCallLedgerRow,
    call_ledger_from_contract,
    describe_contract_call_ledger,
    operator_call_ledger_to_dict,
)
from apc.runtime_contract import default_runtime_execution_contract
from apc.runtime_cpu import RuntimeConfig, run_repair


ROOT = Path(__file__).resolve().parents[1]


class OperatorCallLedgerTests(unittest.TestCase):
    def test_call_ledger_rows_name_contract_steps(self):
        contract = default_runtime_execution_contract()
        ledger = call_ledger_from_contract(contract)

        self.assertEqual(len(ledger.rows), len(contract.steps))
        self.assertEqual(ledger.backend, contract.backend)
        self.assertEqual(ledger.contract_schema, contract.version)
        self.assertEqual(
            [row.step_name for row in ledger.rows],
            [step.name for step in contract.steps],
        )

    def test_call_ledger_is_json_ready(self):
        payload = describe_contract_call_ledger(default_runtime_execution_contract())

        encoded = json.dumps(payload, sort_keys=True)

        self.assertEqual(payload["schema"], "apc.operator_call_ledger.v1")
        self.assertEqual(payload["contract_schema"], "apc.runtime_execution_contract.v1")
        self.assertIn("rows", payload)
        self.assertIn("operator_call_ledger", encoded)

    def test_call_ledger_rows_include_status_backend_and_timing(self):
        payload = describe_contract_call_ledger(default_runtime_execution_contract())

        for row in payload["rows"]:
            with self.subTest(step=row["step_name"]):
                self.assertEqual(row["backend"], "cpu")
                self.assertIn(row["status"], {"implemented", "planned", "skipped", "failed"})
                self.assertTrue(row["timing"])
                self.assertTrue(all(field.endswith("_s") for field in row["timing"]))
                self.assertTrue(row["inputs"])
                self.assertTrue(row["outputs"])

    def test_call_ledger_accepts_factual_timing_values(self):
        contract = default_runtime_execution_contract()
        payload = describe_contract_call_ledger(
            contract,
            timings={
                "eval_constraints": {
                    "kernel_time_s": 0.001,
                    "copy_time_s": 0.0,
                    "layout_conversion_time_s": 0.0,
                    "end_to_end_time_s": 0.002,
                }
            },
            statuses={"eval_constraints": "implemented"},
        )
        rows = {row["step_name"]: row for row in payload["rows"]}

        self.assertEqual(rows["eval_constraints"]["timing"]["kernel_time_s"], 0.001)
        self.assertEqual(rows["eval_constraints"]["timing"]["copy_time_s"], 0.0)

    def test_call_ledger_validation_rejects_bad_timing(self):
        with self.assertRaises(ValueError):
            OperatorCallLedgerRow(
                step_name="bad",
                backend="cpu",
                status="implemented",
                timing={"kernel_time": 0.0},
                inputs=("state.candidate_major",),
                outputs=("state.candidate_major",),
            )
        with self.assertRaises(ValueError):
            OperatorCallLedgerRow(
                step_name="bad",
                backend="cpu",
                status="implemented",
                timing={"kernel_time_s": -1.0},
                inputs=("state.candidate_major",),
                outputs=("state.candidate_major",),
            )

    def test_call_ledger_does_not_change_cpu_runtime_behavior(self):
        spec = load_problem_json(ROOT / "examples" / "specs" / "binary_milp_tiny.json")
        problem = lower_problem_to_ctir(spec, batch_size=4)
        config = RuntimeConfig(max_iters=2, batch_size=4, seed=0)

        before = run_repair(problem, config=config)
        _ = operator_call_ledger_to_dict(call_ledger_from_contract(default_runtime_execution_contract()))
        after = run_repair(problem, config=config)

        self.assertEqual(before.best_state, after.best_state)
        self.assertEqual(before.best_objective, after.best_objective)
        self.assertEqual(before.best_penalty, after.best_penalty)
        self.assertEqual(before.ledger, after.ledger)

    def test_call_ledger_stays_factual_only(self):
        text = json.dumps(describe_contract_call_ledger(default_runtime_execution_contract())).lower()

        self.assertIn("evidence fields", text)
        self.assertNotIn("speedup", text)
        self.assertNotIn("compatible with", text)


if __name__ == "__main__":
    unittest.main()
