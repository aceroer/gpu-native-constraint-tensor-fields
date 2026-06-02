import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG_EXECUTION = ROOT / "docs" / "TAG_EXECUTION_0_2.md"
ARCHIVE = ROOT / "docs" / "RELEASE_ARCHIVE_0_2.md"


class TagExecution02Tests(unittest.TestCase):
    def test_tag_execution_requires_all_evidence_commands(self):
        text = TAG_EXECUTION.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/verify_public_release.py --full", text)
        self.assertIn("python3 scripts/collect_release_artifacts.py --tag v0.2.0-alpha.N", text)
        self.assertIn("python3 scripts/inspect_release_artifacts.py", text)
        self.assertIn("python3 scripts/smoke_release_evidence.py --tag v0.2.0-alpha.N", text)
        self.assertIn("/tmp/apc-release-artifacts-0-2.json", text)
        self.assertIn("/tmp/apc-release-artifacts-summary-0-2.json", text)
        self.assertIn("/tmp/apc-release-evidence-smoke-0-2.json", text)

    def test_tag_execution_requires_commit_match(self):
        text = TAG_EXECUTION.read_text(encoding="utf-8")

        self.assertIn("candidate_commit", text)
        self.assertIn("artifact_commit", text)
        self.assertIn("The two commit hashes must match", text)
        self.assertIn("Candidate commit does not match artifact report commit", text)

    def test_tag_execution_defers_published_tag_claim(self):
        text = TAG_EXECUTION.read_text(encoding="utf-8").lower()

        self.assertIn("not a claim that the tag already exists", text)
        self.assertIn("tag_kind: pending", text)
        self.assertNotIn("tag_commit:", text)
        self.assertNotIn("published tag", text)

    def test_archive_finalization_rules_are_explicit(self):
        text = ARCHIVE.read_text(encoding="utf-8")

        self.assertIn("Tag Verification", text)
        self.assertIn("git rev-parse v0.2.0-alpha.0^{commit}", text)
        self.assertIn("git ls-remote --tags origin 'v0.2.0-alpha.0*'", text)
        self.assertIn("tag: v0.2.0-alpha.0", text)
        self.assertIn("tag_commit: 795e051f92c87b19f7827410f223dea6a7450fcc", text)
        self.assertIn("tag_kind: annotated", text)

    def test_tag_execution_keeps_limits_visible(self):
        text = TAG_EXECUTION.read_text(encoding="utf-8").lower()

        self.assertIn("qubo execution remains planned", text)
        self.assertIn("without complete timing evidence", text)
        self.assertNotIn("compatible with", text)
        self.assertNotIn("guaranteed", text)


if __name__ == "__main__":
    unittest.main()
