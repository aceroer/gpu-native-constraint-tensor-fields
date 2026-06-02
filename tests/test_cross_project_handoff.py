import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "CROSS_PROJECT_HANDOFF.md"
RELEASE_NOTES = ROOT / "docs" / "RELEASE_NOTES_DRAFT.md"
ROADMAP = ROOT / "ROADMAP.md"


class CrossProjectHandoffTests(unittest.TestCase):
    def test_handoff_names_release_tags_and_artifact_schema(self):
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("gpu_tag: v0.1.0-alpha.0", text)
        self.assertIn("gpu_tag_commit: b051c20b38ff19cf99992daa72dc1e9558ec7b84", text)
        self.assertIn("gpu_release_artifact_schema: apc.release_artifacts.v1", text)
        self.assertIn("paired_tag: v0.1.0", text)
        self.assertIn("paired_tag_commit: 69c14675c14fbad0c72f6bb719ac362872446ae7", text)

    def test_handoff_names_stable_public_entry_points(self):
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("StatePool", text)
        self.assertIn("BranchTensor", text)
        self.assertIn("ReductionGate", text)
        self.assertIn("InterfaceProjection", text)
        self.assertIn("docs/API_REFERENCE.md", text)
        self.assertIn("docs/APC_ADAPTER.md", text)
        self.assertIn("docs/TASK_PACKS.md", text)

    def test_handoff_avoids_compatibility_claim(self):
        text = HANDOFF.read_text(encoding="utf-8")
        notes = RELEASE_NOTES.read_text(encoding="utf-8")

        self.assertIn("This is a handoff sketch, not a compatibility claim.", text)
        self.assertIn("drop-in paired runtime compatibility", text)
        self.assertIn("cross-project handoff sketch", notes)
        self.assertIn("without claiming drop-in compatibility", notes)

    def test_roadmap_advances_after_phase_28(self):
        text = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("docs/PHASE28_COMPLETION.md", text)
        self.assertIn("Phase 29", text)
        self.assertIn("The next concrete step is Phase 29", text)


if __name__ == "__main__":
    unittest.main()
