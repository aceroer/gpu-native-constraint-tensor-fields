from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from apc.adapters.vagent_handoff import check_vagent_handoff_report


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "apc" / "adapters" / "vagent_handoff.py"


def sample_report() -> dict:
    return {
        "schema": "vagent.apc_handoff_report.v1",
        "task_count": 1,
        "task_ids": ["task_pack_coding_patch"],
        "dimensions": 4,
        "top_k": 1,
        "artifacts": [
            {
                "schema": "vagent.apc_handoff.v1",
                "source": {
                    "project": "vAgentRT",
                    "task_id": "task_pack_coding_patch",
                    "allowed_actions": ["inspect", "apply_patch", "run_tests"],
                },
                "state_pool": {
                    "batch_size": 3,
                    "n_vars": 4,
                    "alive_count": 3,
                    "scores": [0.0, 1.0, 0.0],
                    "uncertainty": [0.5, 0.0, 0.5],
                    "alive_mask": [True, True, True],
                    "metadata": [
                        {"origin": "vagent_task_action", "action": "inspect"},
                        {"origin": "vagent_task_action", "action": "apply_patch"},
                        {"origin": "vagent_task_action", "action": "run_tests"},
                    ],
                },
                "branch_tensor": {
                    "shape": [3, 1],
                    "alive_count": 3,
                    "routes": [
                        [
                            {
                                "state_index": 0,
                                "route_index": 0,
                                "move_type": "emit_action",
                                "payload": [0],
                                "canonical_key": ["action", [0]],
                                "action": "inspect",
                                "branch_id": "b0",
                                "alive": True,
                            }
                        ],
                        [
                            {
                                "state_index": 1,
                                "route_index": 0,
                                "move_type": "emit_action",
                                "payload": [1],
                                "canonical_key": ["action", [1]],
                                "action": "apply_patch",
                                "branch_id": "b1",
                                "alive": True,
                            }
                        ],
                        [
                            {
                                "state_index": 2,
                                "route_index": 0,
                                "move_type": "emit_action",
                                "payload": [2],
                                "canonical_key": ["action", [2]],
                                "action": "run_tests",
                                "branch_id": "b2",
                                "alive": True,
                            }
                        ],
                    ],
                },
                "reduction_gate": {
                    "top_k": 1,
                    "selected_count": 1,
                    "before_count": 3,
                    "after_count": 1,
                    "branch_efficiency": 1.0 / 3.0,
                    "selected": [
                        {
                            "rank": 0,
                            "state_index": 1,
                            "route_index": 0,
                            "move_type": "emit_action",
                            "payload": [1],
                            "score": 1.0,
                            "uncertainty": 0.0,
                            "reduced_score": 1.0,
                            "energy": -1.0,
                        }
                    ],
                },
                "interface_projection": {
                    "projection": {
                        "kind": "adapter_summary",
                        "reason": "vAgentRT task branches projected into APC public handoff shapes",
                    },
                    "payload": {
                        "task_id": "task_pack_coding_patch",
                        "selected_actions": ["apply_patch"],
                        "selected_count": 1,
                        "source_schema": "vagent.apc_handoff.v1",
                    },
                },
            }
        ],
    }


class VAgentHandoffConsumerTests(unittest.TestCase):
    def test_consumer_projects_report_into_apc_check_schema(self) -> None:
        report = check_vagent_handoff_report(sample_report())

        self.assertEqual(report["schema"], "apc.cross_project_handoff_check.v1")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["source_schema"], "vagent.apc_handoff_report.v1")
        self.assertEqual(report["task_ids"], ["task_pack_coding_patch"])
        artifact = report["artifacts"][0]
        self.assertEqual(artifact["state_pool"]["batch_size"], 3)
        self.assertEqual(artifact["branch_tensor"]["shape"], [3, 1])
        self.assertEqual(artifact["reduction_gate"]["selected_count"], 1)
        self.assertEqual(
            artifact["interface_projection"]["projection"]["kind"],
            "adapter_summary",
        )
        self.assertEqual(artifact["checks"]["reduction_gate_refs"], "ok")

    def test_consumer_rejects_selected_route_out_of_range(self) -> None:
        report = sample_report()
        report["artifacts"][0]["reduction_gate"]["selected"][0]["state_index"] = 99

        with self.assertRaisesRegex(ValueError, "state_index out of range"):
            check_vagent_handoff_report(report)

    def test_script_writes_check_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            handoff = Path(tmpdir) / "handoff.json"
            out = Path(tmpdir) / "check.json"
            handoff.write_text(json.dumps(sample_report()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/check_vagent_handoff.py",
                    str(handoff),
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            stdout_report = json.loads(completed.stdout)
            file_report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(stdout_report["schema"], "apc.cross_project_handoff_check.v1")
            self.assertEqual(file_report["schema"], "apc.cross_project_handoff_check.v1")

    def test_consumer_does_not_import_vagent(self) -> None:
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        self.assertFalse(
            any(name == "vagent" or name.startswith("vagent.") for name in imports)
        )


if __name__ == "__main__":
    unittest.main()
