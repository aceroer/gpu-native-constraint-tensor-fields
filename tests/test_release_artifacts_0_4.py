import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs" / "RELEASE_ARCHIVE_0_4.md"
ARTIFACTS = ROOT / "docs" / "RELEASE_ARTIFACTS.md"


class ReleaseArtifacts04Tests(unittest.TestCase):
    def test_archive_names_required_0_4_evidence(self):
        text = ARCHIVE.read_text(encoding="utf-8")

        self.assertIn("/tmp/apc-release-verify-full-0-4.json", text)
        self.assertIn("/tmp/apc-cuda-parity-report-0-4.json", text)
        self.assertIn("/tmp/apc-runtime-debug-0-4.json", text)
        self.assertIn("/tmp/apc-release-artifacts-0-4.json", text)
        self.assertIn("runtime debug tools", text)
        self.assertIn("0.4 beta debug checkpoint", text)

    def test_archive_is_candidate_until_tag_verified(self):
        text = ARCHIVE.read_text(encoding="utf-8")

        self.assertIn("candidate archive", text)
        self.assertIn("the candidate tag exists", text)
        self.assertIn("tag commit matches release artifact commit", text)

    def test_release_artifacts_doc_keeps_0_4_files(self):
        text = ARTIFACTS.read_text(encoding="utf-8")

        self.assertIn("docs/RELEASE_CHECKLIST_0_4.md", text)
        self.assertIn("docs/RELEASE_NOTES_0_4_DRAFT.md", text)
        self.assertIn("docs/TAG_EXECUTION_0_4.md", text)
        self.assertIn("docs/RELEASE_ARCHIVE_0_4.md", text)
        self.assertIn("tests/test_release_checklist_0_4.py", text)
        self.assertIn("tests/test_release_artifacts_0_4.py", text)


if __name__ == "__main__":
    unittest.main()
