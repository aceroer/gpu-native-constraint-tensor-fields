from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from apc.adapters.vagent_handoff import check_vagent_handoff_report
from scripts.run_checked_handoff_demo import run_checked_handoff_demo
from tests.test_vagent_handoff_consumer import sample_report


ROOT = Path(__file__).resolve().parents[1]


class CheckedHandoffDemoTests(unittest.TestCase):
    def test_demo_consumes_checked_handoff_schema(self) -> None:
        checked = check_vagent_handoff_report(sample_report())

        demo = run_checked_handoff_demo(checked)

        self.assertEqual(demo["schema"], "apc.checked_handoff_runtime_demo.v1")
        self.assertEqual(demo["status"], "ok")
        self.assertEqual(demo["source_schema"], "apc.cross_project_handoff_check.v1")
        self.assertEqual(demo["task_count"], 1)
        self.assertIn("StatePool inspection", demo["runtime_route"])
        task = demo["tasks"][0]
        self.assertEqual(task["task_id"], "task_pack_coding_patch")
        self.assertEqual(task["state_pool"]["batch_size"], 3)
        self.assertEqual(task["branch_tensor"]["shape"], [3, 1])
        self.assertEqual(task["selected_actions"], ["apply_patch"])
        self.assertEqual(task["selected_count"], 1)
        self.assertEqual(task["checks"]["state_pool_present"], "ok")

    def test_demo_rejects_unchecked_source_report(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected schema"):
            run_checked_handoff_demo(sample_report())

    def test_script_writes_demo_report(self) -> None:
        checked = check_vagent_handoff_report(sample_report())
        with tempfile.TemporaryDirectory() as tmpdir:
            check_path = Path(tmpdir) / "checked.json"
            out_path = Path(tmpdir) / "demo.json"
            check_path.write_text(json.dumps(checked), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_checked_handoff_demo.py",
                    str(check_path),
                    "--out",
                    str(out_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            stdout_report = json.loads(completed.stdout)
            file_report = json.loads(out_path.read_text(encoding="utf-8"))

        self.assertEqual(stdout_report["schema"], "apc.checked_handoff_runtime_demo.v1")
        self.assertEqual(file_report["source_schema"], "apc.cross_project_handoff_check.v1")

    def test_demo_keeps_non_compatibility_boundary_visible(self) -> None:
        checked = check_vagent_handoff_report(sample_report())
        demo = run_checked_handoff_demo(checked)
        notes = "\n".join(demo["notes"])

        self.assertIn("not a drop-in runtime compatibility claim", notes)


if __name__ == "__main__":
    unittest.main()
