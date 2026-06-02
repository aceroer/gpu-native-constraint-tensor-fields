from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "examples" / "handoff"
SOURCE = FIXTURE_DIR / "vagent_binary_milp_handoff_report.v1.json"
CHECKED = FIXTURE_DIR / "apc_binary_milp_handoff_check.v1.json"
DEMO = FIXTURE_DIR / "apc_binary_milp_checked_handoff_demo.v1.json"


class ProblemFamilyHandoffFixtureTests(unittest.TestCase):
    def test_fixture_names_public_problem_family(self) -> None:
        source = _load(SOURCE)
        checked = _load(CHECKED)
        demo = _load(DEMO)

        self.assertEqual(source["problem_family"], "binary_milp")
        self.assertEqual(checked["artifacts"][0]["source"]["problem_family"], "binary_milp")
        self.assertEqual(demo["tasks"][0]["problem_family"], "binary_milp")
        self.assertEqual(demo["tasks"][0]["selected_actions"], ["propose_bit_flip"])

    def test_checked_fixture_matches_check_script_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "check.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/check_vagent_handoff.py",
                    str(SOURCE),
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
            file_report = _load(out)

        expected = _load(CHECKED)
        self.assertEqual(stdout_report, expected)
        self.assertEqual(file_report, expected)

    def test_demo_fixture_matches_demo_script_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "demo.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_checked_handoff_demo.py",
                    str(CHECKED),
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
            file_report = _load(out)

        expected = _load(DEMO)
        self.assertEqual(stdout_report, expected)
        self.assertEqual(file_report, expected)

    def test_fixture_keeps_json_only_boundary_visible(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in (CHECKED, DEMO))

        self.assertIn("does not import vAgentRT", text)
        self.assertIn("not a drop-in compatibility claim", text)
        self.assertIn("not a drop-in runtime compatibility claim", text)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
