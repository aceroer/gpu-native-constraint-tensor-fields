import json
import subprocess
import sys
import unittest
from pathlib import Path

from apc import default_operator_registry, registry_summary
from apc.operators_cpu import eval_constraints


ROOT = Path(__file__).resolve().parents[1]


class OperatorRegistryTests(unittest.TestCase):
    def test_registry_contains_cpu_references_and_cuda_symbols(self):
        summary = registry_summary()
        operators = {operator["name"]: operator for operator in summary["operators"]}

        self.assertIn("eval_constraints", operators)
        self.assertEqual(operators["eval_constraints"]["cpu_reference"], "apc.operators_cpu.eval_constraints")
        self.assertEqual(operators["eval_constraints"]["cuda_symbol"], "apc_eval_linear_csr")
        self.assertIn("apc_eval_clause_csr", summary["cuda_symbols"])

    def test_registered_cpu_reference_is_importable(self):
        registry = default_operator_registry()
        eval_spec = [operator for operator in registry if operator.name == "eval_constraints"][0]

        self.assertEqual(eval_spec.cpu_reference, f"{eval_constraints.__module__}.{eval_constraints.__name__}")

    def test_registry_summary_is_json_ready(self):
        payload = json.loads(json.dumps(registry_summary(), sort_keys=True))

        self.assertIn("operators", payload)
        self.assertIn("backends", payload)
        self.assertIn("cuda_symbols", payload)
        self.assertIn("cpu", payload["backends"])

    def test_cli_prints_operator_registry(self):
        completed = subprocess.run(
            [sys.executable, "-m", "apc.cli", "operators"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        names = {operator["name"] for operator in payload["operators"]}
        self.assertIn("eval_clauses", names)
        self.assertIn("apply_projection", names)


if __name__ == "__main__":
    unittest.main()
