import unittest

from apc import (
    interface_projection_to_dict,
    project_public_summary,
    project_runtime_summary,
)
from apc.adapters import adapter_result_to_dict
from apc.io_json import load_problem_json, problem_to_json_dict
from apc.adapters import lower_native_binary_milp_dict


class InterfaceProjectionTests(unittest.TestCase):
    def test_public_projection_includes_reason_and_payload(self):
        projection = project_public_summary(
            "state_pool_summary",
            {"batch_size": 2},
            reason="state pool projected for JSON inspection",
        )

        data = interface_projection_to_dict(projection)

        self.assertEqual(data["projection"]["kind"], "state_pool_summary")
        self.assertEqual(data["projection"]["reason"], "state pool projected for JSON inspection")
        self.assertEqual(data["payload"]["batch_size"], 2)

    def test_runtime_projection_keeps_runtime_state_outside_api_shape(self):
        projection = project_runtime_summary(
            {"selected_count": 1},
            reason="reduction result projected for ledger output",
        )
        data = interface_projection_to_dict(projection)

        self.assertEqual(set(data), {"projection", "payload"})
        self.assertEqual(data["payload"], {"selected_count": 1})

    def test_adapter_summary_uses_projection_helper(self):
        problem = load_problem_json("examples/specs/binary_milp_tiny.json")
        result = lower_native_binary_milp_dict(problem_to_json_dict(problem), batch_size=2)

        data = adapter_result_to_dict(result)

        self.assertEqual(data["projection"]["kind"], "adapter_summary")
        self.assertIn("native problem", data["projection"]["reason"])
        self.assertEqual(data["payload"]["batch_size"], 2)
        self.assertIn("linear.csr", data["payload"]["layout_views"])

    def test_projection_requires_reason(self):
        with self.assertRaisesRegex(ValueError, "reason"):
            project_public_summary("summary", {}, reason="")


if __name__ == "__main__":
    unittest.main()
