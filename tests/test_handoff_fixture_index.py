from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "examples" / "handoff"
INDEX = FIXTURE_DIR / "README.md"


FIXTURE_SETS = (
    (
        "vagent_apc_handoff_report.v1.json",
        "apc_handoff_check.v1.json",
        "apc_checked_handoff_demo.v1.json",
        None,
    ),
    (
        "vagent_binary_milp_handoff_report.v1.json",
        "apc_binary_milp_handoff_check.v1.json",
        "apc_binary_milp_checked_handoff_demo.v1.json",
        "binary_milp",
    ),
)


class HandoffFixtureIndexTests(unittest.TestCase):
    def test_index_names_each_fixture_file(self) -> None:
        text = INDEX.read_text(encoding="utf-8")

        for source, checked, demo, _family in FIXTURE_SETS:
            self.assertIn(source, text)
            self.assertIn(checked, text)
            self.assertIn(demo, text)

    def test_index_records_schema_names(self) -> None:
        text = INDEX.read_text(encoding="utf-8")

        self.assertIn("apc.problem_family_fixture_index.v1", text)
        self.assertIn("vagent.apc_handoff_report.v1", text)
        self.assertIn("apc.cross_project_handoff_check.v1", text)
        self.assertIn("apc.checked_handoff_runtime_demo.v1", text)

    def test_index_problem_families_match_json(self) -> None:
        text = INDEX.read_text(encoding="utf-8")

        self.assertIn("problem_families: binary_milp, maxsat, qubo", text)
        self.assertIn("problem_family: none", text)
        self.assertIn("problem_family: binary_milp", text)
        family_index = _load(FIXTURE_DIR / "problem_family_fixtures.v1.json")
        source = _load(FIXTURE_DIR / "vagent_binary_milp_handoff_report.v1.json")
        demo = _load(FIXTURE_DIR / "apc_binary_milp_checked_handoff_demo.v1.json")
        self.assertEqual(family_index["schema"], "apc.problem_family_fixture_index.v1")
        self.assertEqual(source["problem_family"], "binary_milp")
        self.assertEqual(demo["tasks"][0]["problem_family"], "binary_milp")

    def test_index_keeps_boundary_visible(self) -> None:
        text = INDEX.read_text(encoding="utf-8")

        self.assertIn("JSON-only", text)
        self.assertIn("not a compatibility promise", text)
        self.assertIn("No paired-project import", text)
        self.assertIn("No stable adapter ABI claim", text)
        self.assertIn("No GPU speedup claim", text)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
