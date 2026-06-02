import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.list_problem_family_fixtures import list_problem_family_fixtures


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "examples" / "handoff" / "problem_family_fixtures.v1.json"


class ProblemFamilyFixtureSetTests(unittest.TestCase):
    def test_fixture_index_lists_all_problem_families(self):
        payload = _load(INDEX)
        families = {fixture["family"] for fixture in payload["fixtures"]}

        self.assertEqual(payload["schema"], "apc.problem_family_fixture_index.v1")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["fixture_count"], 3)
        self.assertEqual(families, {"binary_milp", "maxsat", "qubo"})

    def test_fixture_records_name_schema_status_and_command(self):
        payload = _load(INDEX)

        for fixture in payload["fixtures"]:
            with self.subTest(fixture=fixture["name"]):
                self.assertTrue(fixture["name"])
                self.assertTrue(fixture["spec_schema"].startswith("apc."))
                self.assertIn(fixture["route_status"], {"implemented", "planned"})
                self.assertIn(fixture["execution_status"], {"implemented", "planned"})
                self.assertTrue(fixture["command"].startswith("PYTHONPATH=src"))
                self.assertTrue(fixture["exists"])

    def test_implemented_routes_include_checked_reports(self):
        payload = _load(INDEX)
        reports = {fixture["family"]: fixture["checked_report"] for fixture in payload["fixtures"]}

        self.assertEqual(reports["binary_milp"]["schema"], "apc.benchmark.v1")
        self.assertEqual(reports["binary_milp"]["status"], "implemented")
        self.assertEqual(reports["maxsat"]["schema"], "apc.maxsat_runtime_route.v1")
        self.assertEqual(reports["maxsat"]["status"], "implemented")
        self.assertEqual(reports["qubo"]["schema"], "apc.qubo_lowering.v1")
        self.assertEqual(reports["qubo"]["status"], "implemented")

    def test_planned_execution_routes_remain_marked_planned(self):
        payload = _load(INDEX)
        fixtures = {fixture["family"]: fixture for fixture in payload["fixtures"]}

        self.assertEqual(fixtures["qubo"]["execution_status"], "planned")
        self.assertEqual(fixtures["qubo"]["checked_report"]["execution_status"], "planned")
        self.assertEqual(fixtures["binary_milp"]["execution_status"], "implemented")
        self.assertEqual(fixtures["maxsat"]["execution_status"], "implemented")

    def test_script_reproduces_fixture_index_shape(self):
        generated = list_problem_family_fixtures()
        static = _load(INDEX)

        self.assertEqual(generated["schema"], static["schema"])
        self.assertEqual(generated["status"], static["status"])
        self.assertEqual(
            [(item["family"], item["spec"], item["checked_report"]["schema"]) for item in generated["fixtures"]],
            [(item["family"], item["spec"], item["checked_report"]["schema"]) for item in static["fixtures"]],
        )

    def test_script_writes_fixture_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "fixtures.json"
            completed = subprocess.run(
                [sys.executable, "scripts/list_problem_family_fixtures.py", "--out", str(out)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            stdout_report = json.loads(completed.stdout)
            file_report = _load(out)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(stdout_report["schema"], "apc.problem_family_fixture_index.v1")
        self.assertEqual(file_report["fixture_count"], 3)

    def test_fixture_docs_avoid_claims(self):
        text = (ROOT / "docs" / "PROBLEM_FAMILIES.md").read_text(encoding="utf-8")
        payload_text = json.dumps(_load(INDEX)).lower()

        self.assertIn("apc.problem_family_fixture_index.v1", text)
        self.assertIn("not claim", text)
        self.assertNotIn("compatible with", text.lower())
        self.assertNotIn("speedup", text.lower())
        self.assertNotIn("compatible with", payload_text)
        self.assertNotIn("speedup", payload_text)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
