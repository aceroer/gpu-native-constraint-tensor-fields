import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vector_state_repair import run_vector_state_repair_demo


class VectorStateRepairDemoTests(unittest.TestCase):
    def test_demo_runs_through_public_state_pool_path(self):
        report = run_vector_state_repair_demo(
            "examples/specs/binary_milp_tiny.json",
            batch_size=3,
            top_k=2,
        )
        payload = report["payload"]

        self.assertEqual(report["projection"]["kind"], "runtime_summary")
        self.assertIn("state pool", report["projection"]["reason"])
        self.assertEqual(payload["state_pool"]["batch_size"], 3)
        self.assertEqual(payload["branch_tensor"]["shape"], [3, 3])
        self.assertEqual(payload["reduction"]["selected_count"], 2)

    def test_demo_report_contains_required_metrics(self):
        report = run_vector_state_repair_demo("examples/specs/binary_milp_tiny.json")
        metrics = report["payload"]["metrics"]

        self.assertEqual(metrics["branch_count"], 12)
        self.assertEqual(metrics["selected_action_count"], 2)
        self.assertIs(metrics["success"], True)

    def test_demo_cli_writes_reproducible_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "report.json"
            subprocess.run(
                [
                    sys.executable,
                    "examples/vector_state_repair/run_demo.py",
                    "examples/specs/binary_milp_tiny.json",
                    "--out",
                    str(out),
                    "--batch-size",
                    "2",
                    "--top-k",
                    "1",
                ],
                check=True,
                env={
                    "PYTHONPATH": os.pathsep.join(["src", "examples/vector_state_repair"]),
                },
                stdout=subprocess.PIPE,
                text=True,
            )
            data = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(data["payload"]["metrics"]["branch_count"], 6)
        self.assertEqual(data["payload"]["metrics"]["selected_action_count"], 1)
        self.assertIs(data["payload"]["metrics"]["success"], True)


if __name__ == "__main__":
    unittest.main()
