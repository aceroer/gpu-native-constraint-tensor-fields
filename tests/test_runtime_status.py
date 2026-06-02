import json
import unittest

from apc.operator_call_ledger import OperatorCallLedgerRow, describe_contract_call_ledger
from apc.runtime_contract import default_runtime_execution_contract
from apc.runtime_status import (
    FAILED,
    IMPLEMENTED,
    PLANNED,
    SKIPPED,
    UNAVAILABLE,
    default_runtime_status_codes,
    is_runtime_status_code,
    runtime_status_code_map,
    runtime_status_codes_to_dict,
)


class RuntimeStatusTests(unittest.TestCase):
    def test_status_codes_are_stable_public_strings(self):
        codes = default_runtime_status_codes()
        names = [row.code for row in codes]

        self.assertEqual(names, [IMPLEMENTED, PLANNED, SKIPPED, FAILED, UNAVAILABLE])
        self.assertEqual(len(names), len(set(names)))
        for name in names:
            self.assertEqual(name, name.lower())
            self.assertNotIn(" ", name)

    def test_status_code_records_are_json_ready(self):
        payload = runtime_status_codes_to_dict()

        encoded = json.dumps(payload, sort_keys=True)

        self.assertEqual(payload["schema"], "apc.runtime_status_codes.v1")
        self.assertIn("codes", payload)
        self.assertIn("implemented", encoded)
        self.assertIn("unavailable", encoded)

    def test_status_code_map_resolves_terminal_failure(self):
        code_map = runtime_status_code_map()

        self.assertFalse(code_map[IMPLEMENTED].terminal)
        self.assertTrue(code_map[FAILED].terminal)
        self.assertEqual(code_map[UNAVAILABLE].category, "environment")

    def test_operator_call_ledger_references_status_codes(self):
        payload = describe_contract_call_ledger(
            default_runtime_execution_contract(),
            statuses={"eval_constraints": UNAVAILABLE},
        )
        status_codes = set(runtime_status_code_map())

        for row in payload["rows"]:
            with self.subTest(step=row["step_name"]):
                self.assertIn(row["status"], status_codes)
        rows = {row["step_name"]: row for row in payload["rows"]}
        self.assertEqual(rows["eval_constraints"]["status"], UNAVAILABLE)

    def test_operator_call_ledger_rejects_unknown_status_code(self):
        with self.assertRaises(ValueError):
            OperatorCallLedgerRow(
                step_name="bad",
                backend="cpu",
                status="unknown",
                timing={"kernel_time_s": 0.0},
                inputs=("state.candidate_major",),
                outputs=("state.candidate_major",),
            )

    def test_status_records_stay_factual_only(self):
        text = json.dumps(runtime_status_codes_to_dict()).lower()

        self.assertIn("factual runtime evidence labels", text)
        self.assertFalse(is_runtime_status_code("unknown"))
        self.assertNotIn("compatible with", text)
        self.assertNotIn("drop-in", text)


if __name__ == "__main__":
    unittest.main()
