import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CHECKLIST = DOCS / "RELEASE_CHECKLIST_0_3.md"
NOTES = DOCS / "RELEASE_NOTES_0_3_DRAFT.md"
ARCHIVE = DOCS / "RELEASE_ARCHIVE_0_3.md"
TAG_EXECUTION = DOCS / "TAG_EXECUTION_0_3.md"


class ReleaseChecklist03Tests(unittest.TestCase):
    def test_checklist_names_required_evidence_commands(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/verify_public_release.py --full", text)
        self.assertIn("python3 scripts/collect_release_artifacts.py --tag v0.3.0-alpha.N", text)
        self.assertIn("python3 scripts/smoke_release_evidence.py --tag v0.3.0-alpha.N", text)
        self.assertIn("benchmarks/sweeps/qubo_smoke.json", text)
        self.assertIn("benchmarks/sweeps/maxsat_smoke.json", text)
        self.assertIn("tests.cuda.test_qubo_energy", text)
        self.assertIn("tests.cuda.test_clause_eval", text)

    def test_checklist_names_0_3_gates(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        for item in (
            "src/apc/runtime_qubo_cpu.py",
            "tests/test_qubo_cpu_reference.py",
            "src/apc/readings/maxsat.py",
            "tests/test_maxsat_runtime_route.py",
            "docs/CUDA_OPERATOR_PARITY.md",
            "tests/cuda/test_parity_target_selection.py",
            "tests/cuda/test_qubo_energy.py",
            "tests/cuda/test_clause_eval.py",
            "examples/handoff/problem_family_fixtures.v1.json",
        ):
            self.assertIn(item, text)

    def test_checklist_names_required_public_schemas(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        for schema in (
            "apc.public_release_verification.v1",
            "apc.release_artifacts.v1",
            "apc.release_artifacts_summary.v1",
            "apc.release_evidence_smoke.v1",
            "apc.qubo_cpu_reference_execution.v1",
            "apc.maxsat_runtime_route.v1",
            "apc.benchmark_sweep.v1",
            "apc.problem_family_fixture_index.v1",
        ):
            self.assertIn(schema, text)

    def test_notes_and_archive_state_limits(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in (NOTES, ARCHIVE))

        self.assertIn("0.3 Reference-First Runtime Expansion", text)
        self.assertIn("QUBO CPU reference execution route", text)
        self.assertIn("MaxSAT deterministic ledger-ready CPU route", text)
        self.assertIn("No drop-in replacement for existing solvers", text)
        self.assertIn("without complete timing evidence", text)
        self.assertIn("candidate_tag: v0.3.0-alpha.N", text)
        self.assertIn("tag_kind: pending", text)

    def test_tag_execution_defers_published_tag_claim(self):
        text = TAG_EXECUTION.read_text(encoding="utf-8").lower()

        self.assertIn("not a claim that the tag already exists", text)
        self.assertIn("candidate_commit", text)
        self.assertIn("artifact_commit", text)
        self.assertIn("the two commit hashes must match", text)
        self.assertIn("tag_kind: pending", text)
        self.assertNotIn("tag_commit:", text)

    def test_0_3_docs_avoid_unearned_claims(self):
        text = "\n".join(
            path.read_text(encoding="utf-8") for path in (CHECKLIST, NOTES, ARCHIVE, TAG_EXECUTION)
        ).lower()

        self.assertNotIn("compatible with", text)
        self.assertNotIn("guaranteed", text)
        self.assertNotIn("speedup", text)


if __name__ == "__main__":
    unittest.main()
