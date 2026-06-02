import unittest

from apc.adapters import adapter_result_to_dict, lower_native_binary_milp_dict
from apc.io_json import load_problem_json, problem_to_json_dict


class AdapterTests(unittest.TestCase):
    def test_native_dict_adapter_goes_through_layout_and_registry(self):
        problem = load_problem_json("examples/specs/binary_milp_tiny.json")
        data = problem_to_json_dict(problem)

        result = lower_native_binary_milp_dict(data, batch_size=3)
        summary = adapter_result_to_dict(result)

        self.assertEqual(summary["source"], "native_binary_milp_dict")
        self.assertEqual(summary["batch_size"], 3)
        self.assertIn("linear.csr", summary["layout_views"])
        self.assertIn("state.variable_major", summary["layout_views"])
        self.assertIn("eval_constraints", summary["operators"])
        self.assertIn("record_metrics", summary["operators"])

    def test_unsupported_solver_features_fail_loudly(self):
        problem = load_problem_json("examples/specs/binary_milp_tiny.json")
        data = problem_to_json_dict(problem)
        data["solver"] = {"name": "external"}

        with self.assertRaisesRegex(ValueError, "unsupported adapter features: solver"):
            lower_native_binary_milp_dict(data)


if __name__ == "__main__":
    unittest.main()
