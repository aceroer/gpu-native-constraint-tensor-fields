from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.list_handoff_fixtures import list_handoff_fixtures


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "list_handoff_fixtures.py"


class HandoffFixtureListingTests(unittest.TestCase):
    def test_listing_emits_fixture_metadata(self) -> None:
        report = list_handoff_fixtures()

        self.assertEqual(report["schema"], "apc.handoff_fixture_index.v1")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["fixture_count"], 2)
        names = [item["name"] for item in report["fixtures"]]
        self.assertEqual(names, ["generic_task_pack", "binary_milp"])
        binary = report["fixtures"][1]
        self.assertEqual(binary["problem_family"], "binary_milp")
        self.assertEqual(binary["schemas"]["source"], "vagent.apc_handoff_report.v1")
        self.assertEqual(binary["schemas"]["checked"], "apc.cross_project_handoff_check.v1")
        self.assertEqual(binary["schemas"]["demo"], "apc.checked_handoff_runtime_demo.v1")

    def test_script_writes_listing_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "fixtures.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/list_handoff_fixtures.py",
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

        self.assertEqual(stdout_report, file_report)
        self.assertEqual(file_report["schema"], "apc.handoff_fixture_index.v1")

    def test_listing_keeps_boundary_visible(self) -> None:
        report = list_handoff_fixtures()
        notes = "\n".join(report["notes"])

        self.assertIn("inspection evidence only", notes)
        self.assertIn("does not import paired projects", notes)
        self.assertIn("claim compatibility", notes)

    def test_listing_script_does_not_import_paired_project(self) -> None:
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
