import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CHECKLIST = DOCS / "RELEASE_CHECKLIST_0_2.md"
NOTES = DOCS / "RELEASE_NOTES_0_2_DRAFT.md"


class ReleaseChecklist02Tests(unittest.TestCase):
    def test_checklist_names_required_evidence_commands(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/verify_public_release.py --full", text)
        self.assertIn("python3 scripts/collect_release_artifacts.py", text)
        self.assertIn("python3 scripts/smoke_release_evidence.py", text)
        self.assertIn("/tmp/apc-release-verify-full.json", text)
        self.assertIn("/tmp/apc-release-artifacts-0-2.json", text)
        self.assertIn("/tmp/apc-release-evidence-smoke-0-2.json", text)

    def test_checklist_names_native_runtime_buildout_gates(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        for item in (
            "docs/RUNTIME_CONTRACT.md",
            "native/include/apc_runtime.hpp",
            "native/src/cpu_operator_shim.cpp",
            "docs/CUDA_OPERATOR_PARITY.md",
            "benchmarks/sweeps/binary_milp_smoke.json",
            "scripts/run_benchmark_sweep.py",
            "scripts/inspect_benchmark_sweep.py",
            "examples/handoff/problem_family_fixtures.v1.json",
            "scripts/list_problem_family_fixtures.py",
            "tests/test_problem_family_fixture_set.py",
        ):
            self.assertIn(item, text)

    def test_checklist_names_required_public_schemas(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        for schema in (
            "apc.public_release_verification.v1",
            "apc.release_artifacts.v1",
            "apc.release_artifacts_summary.v1",
            "apc.release_evidence_smoke.v1",
            "apc.benchmark_sweep.v1",
            "apc.benchmark_sweep_summary.v1",
            "apc.problem_family_fixture_index.v1",
        ):
            self.assertIn(schema, text)

    def test_release_notes_state_limits_and_non_goals(self):
        text = NOTES.read_text(encoding="utf-8")

        self.assertIn("0.2 Native Runtime Buildout", text)
        self.assertIn("QUBO execution is planned", text)
        self.assertIn("No drop-in replacement for existing solvers", text)
        self.assertIn("No broad accelerator comparison claim", text)
        self.assertIn("QUBO execution only after a tested CPU reference route exists", text)

    def test_checklist_and_notes_avoid_unearned_claims(self):
        text = (CHECKLIST.read_text(encoding="utf-8") + "\n" + NOTES.read_text(encoding="utf-8")).lower()

        self.assertIn("without complete timing evidence", text)
        self.assertNotIn("compatible with", text)
        self.assertNotIn("guaranteed", text)


if __name__ == "__main__":
    unittest.main()
