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
        self.assertIn("paired_tag: v0.1.1", text)
        self.assertIn("paired_tag_commit: 3cb8043979ac3639dc9ef400abe68da9908d03f6", text)
        self.assertIn("paired_cuda_smoke: Colab T4 deterministic smoke status ok", text)

    def test_handoff_names_stable_public_entry_points(self):
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("StatePool", text)
        self.assertIn("BranchTensor", text)
        self.assertIn("ReductionGate", text)
        self.assertIn("InterfaceProjection", text)
        self.assertIn("docs/API_REFERENCE.md", text)
        self.assertIn("docs/APC_ADAPTER.md", text)
        self.assertIn("docs/TASK_PACKS.md", text)
        self.assertIn("vagent.apc_handoff_report.v1", text)
        self.assertIn("scripts/run_apc_handoff.py", text)

    def test_handoff_avoids_compatibility_claim(self):
        text = HANDOFF.read_text(encoding="utf-8")
        notes = RELEASE_NOTES.read_text(encoding="utf-8")

        self.assertIn("This is a handoff sketch, not a compatibility claim.", text)
        self.assertIn("kernel-equivalence evidence, not a speedup claim", text)
        self.assertIn("drop-in paired runtime compatibility", text)
        self.assertIn("cross-project handoff sketch", notes)
        self.assertIn("without claiming drop-in compatibility", notes)

    def test_roadmap_advances_after_phase_28(self):
        text = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("docs/PHASE28_COMPLETION.md", text)
        self.assertIn("Phase 29", text)
        self.assertIn("docs/PHASE29_COMPLETION.md", text)
        self.assertIn("Phase 30", text)
        self.assertIn("docs/PHASE30_COMPLETION.md", text)
        self.assertIn("Phase 31", text)
        self.assertIn("docs/PHASE31_COMPLETION.md", text)
        self.assertIn("Phase 32", text)
        self.assertIn("docs/PHASE32_COMPLETION.md", text)
        self.assertIn("Phase 33", text)
        self.assertIn("docs/PHASE33_COMPLETION.md", text)
        self.assertIn("Phase 34", text)
        self.assertIn("docs/PHASE34_COMPLETION.md", text)
        self.assertIn("Phase 35", text)
        self.assertIn("docs/PHASE35_COMPLETION.md", text)
        self.assertIn("Phase 36", text)
        self.assertIn("docs/PHASE36_COMPLETION.md", text)
        self.assertIn("Phase 50", text)
        self.assertIn("docs/PHASE50_COMPLETION.md", text)
        self.assertIn("Phase 51", text)
        self.assertIn("docs/PHASE51_COMPLETION.md", text)
        self.assertIn("Phase 52", text)
        self.assertIn("The next concrete step is Phase 52", text)


if __name__ == "__main__":
    unittest.main()
