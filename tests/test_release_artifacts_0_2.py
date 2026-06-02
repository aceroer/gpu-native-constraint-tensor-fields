import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "docs" / "RELEASE_ARTIFACTS.md"
ARCHIVE = ROOT / "docs" / "RELEASE_ARCHIVE_0_2.md"
CHECKLIST = ROOT / "docs" / "RELEASE_CHECKLIST_0_2.md"
NOTES = ROOT / "docs" / "RELEASE_NOTES_0_2_DRAFT.md"


class ReleaseArtifacts02Tests(unittest.TestCase):
    def test_artifact_doc_names_0_2_collection_commands(self):
        text = ARTIFACTS.read_text(encoding="utf-8")

        self.assertIn("0.2 Candidate Artifacts", text)
        self.assertIn("python3 scripts/verify_public_release.py --full", text)
        self.assertIn("python3 scripts/collect_release_artifacts.py --tag v0.2.0-alpha.N", text)
        self.assertIn("python3 scripts/inspect_release_artifacts.py", text)
        self.assertIn("python3 scripts/smoke_release_evidence.py --tag v0.2.0-alpha.N", text)
        self.assertIn("scripts/run_benchmark_sweep.py", text)
        self.assertIn("scripts/list_problem_family_fixtures.py", text)

    def test_artifact_doc_names_0_2_required_outputs(self):
        text = ARTIFACTS.read_text(encoding="utf-8")

        for path in (
            "/tmp/apc-release-verify-full.json",
            "/tmp/apc-release-artifacts-0-2.json",
            "/tmp/apc-release-artifacts-summary-0-2.json",
            "/tmp/apc-release-evidence-smoke-0-2.json",
            "/tmp/apc-benchmark-sweep.json",
            "/tmp/apc-benchmark-sweep-summary.json",
            "/tmp/apc-problem-family-fixtures.json",
        ):
            self.assertIn(path, text)

    def test_archive_records_final_tag_and_commit_field(self):
        text = ARCHIVE.read_text(encoding="utf-8")

        self.assertIn("tag: v0.2.0-alpha.0", text)
        self.assertIn("tag_commit: 795e051f92c87b19f7827410f223dea6a7450fcc", text)
        self.assertIn("tag_kind: annotated", text)
        self.assertIn("This document is the durable handoff archive", text)

    def test_archive_draft_names_required_evidence_schemas(self):
        text = ARCHIVE.read_text(encoding="utf-8")

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

    def test_archive_records_verified_tag_without_unchecked_claims(self):
        text = ARCHIVE.read_text(encoding="utf-8").lower()

        self.assertIn("tag verification", text)
        self.assertIn("remote peeled tag commit", text)
        self.assertIn("tag_commit:", text)
        self.assertNotIn("archived_tag:", text)
        self.assertNotIn("candidate_tag:", text)
        self.assertNotIn("pending", text)

    def test_0_2_docs_keep_limits_visible(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in (ARCHIVE, CHECKLIST, NOTES)).lower()

        self.assertIn("qubo execution", text)
        self.assertIn("planned", text)
        self.assertIn("without complete timing evidence", text)
        self.assertNotIn("compatible with", text)
        self.assertNotIn("drop-in replacement for existing solvers is provided", text)


if __name__ == "__main__":
    unittest.main()
