import json
import unittest

from apc.operator_registry import default_operator_registry
from apc.runtime_contract import (
    DEFAULT_TIMING_FIELDS,
    RuntimeExecutionContract,
    RuntimeStepSpec,
    default_runtime_execution_contract,
    describe_cpu_runtime_contract,
    runtime_contract_to_dict,
)


class RuntimeContractTests(unittest.TestCase):
    def test_default_contract_is_json_ready(self):
        contract = default_runtime_execution_contract()
        payload = runtime_contract_to_dict(contract)

        encoded = json.dumps(payload, sort_keys=True)

        self.assertEqual(payload["schema"], "apc.runtime_execution_contract.v1")
        self.assertEqual(payload["backend"], "cpu")
        self.assertIn("binary_milp", payload["problem_families"])
        self.assertIn("maxsat", payload["problem_families"])
        self.assertIn("runtime_execution_contract", encoded)

    def test_runtime_steps_have_contract_fields(self):
        contract = default_runtime_execution_contract()

        for step in contract.steps:
            with self.subTest(step=step.name):
                self.assertTrue(step.inputs)
                self.assertTrue(step.outputs)
                self.assertIn(step.status, {"implemented", "planned", "skipped"})
                self.assertTrue(step.timing_fields)
                self.assertTrue(all(field.endswith("_s") for field in step.timing_fields))

    def test_contract_names_cpu_runtime_sequence_without_changing_behavior(self):
        payload = describe_cpu_runtime_contract()
        step_names = [step["name"] for step in payload["steps"]]

        self.assertIn("lower_problem_to_ctir", step_names)
        self.assertIn("eval_constraints", step_names)
        self.assertIn("rectify_violations", step_names)
        self.assertIn("reduce_penalty", step_names)
        self.assertIn("record_metrics", step_names)
        self.assertIn("reduce_best", step_names)
        self.assertIn("generate_branch_tensor", step_names)
        self.assertIn("select_reduction_gate_actions", step_names)
        self.assertIn("project_public_summary", step_names)

    def test_operator_steps_reference_registered_operator_names(self):
        registry_names = {operator.name for operator in default_operator_registry()}
        contract = default_runtime_execution_contract()

        for step in contract.steps:
            if step.operator_name is None:
                continue
            with self.subTest(step=step.name):
                self.assertIn(step.operator_name, registry_names)

    def test_contract_keeps_timing_fields_explicit(self):
        contract = default_runtime_execution_contract()
        all_fields = {field for step in contract.steps for field in step.timing_fields}

        self.assertTrue(set(DEFAULT_TIMING_FIELDS).issubset(all_fields))
        self.assertIn("layout_conversion_time_s", all_fields)
        self.assertIn("end_to_end_time_s", all_fields)

    def test_contract_validation_rejects_incomplete_steps(self):
        with self.assertRaises(ValueError):
            RuntimeStepSpec(
                name="bad",
                kind="operator",
                inputs=(),
                outputs=("state.candidate_major",),
                status="implemented",
            )
        with self.assertRaises(ValueError):
            RuntimeStepSpec(
                name="bad_timing",
                kind="operator",
                inputs=("state.candidate_major",),
                outputs=("state.candidate_major",),
                status="implemented",
                timing_fields=("kernel_time",),
            )

    def test_contract_validation_rejects_duplicate_step_names(self):
        step = RuntimeStepSpec(
            name="same",
            kind="operator",
            inputs=("state.candidate_major",),
            outputs=("state.candidate_major",),
            status="implemented",
        )

        with self.assertRaises(ValueError):
            RuntimeExecutionContract(
                name="bad_contract",
                version="apc.runtime_execution_contract.v1",
                backend="cpu",
                problem_families=("binary_milp",),
                steps=(step, step),
                non_goals=(),
            )

    def test_contract_does_not_make_solver_compatibility_promise(self):
        text = json.dumps(describe_cpu_runtime_contract()).lower()

        self.assertIn("outside this runtime contract", text)
        self.assertNotIn("compatible with", text)
        self.assertNotIn("replacement for", text)


if __name__ == "__main__":
    unittest.main()
