import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG_PREP = ROOT / "docs" / "TAG_PREP.md"
RELEASE_NOTES = ROOT / "docs" / "RELEASE_NOTES_DRAFT.md"
ROADMAP = ROOT / "ROADMAP.md"


class TagPrepTests(unittest.TestCase):
    def test_tag_prep_references_verifier_and_artifact_collector(self):
        text = TAG_PREP.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/verify_public_release.py --full", text)
        self.assertIn("python3 scripts/collect_release_artifacts.py", text)
        self.assertIn("/tmp/apc-release-verify-full.json", text)
        self.assertIn("/tmp/apc-release-artifacts.json", text)
        self.assertIn("apc.release_artifacts.v1", text)

    def test_release_notes_name_candidate_tag_and_commit_fields(self):
        text = RELEASE_NOTES.read_text(encoding="utf-8")

        self.assertIn("candidate_tag: v0.1.0-alpha.0", text)
        self.assertIn("verified_commit:", text)
        self.assertIn("release_artifact_report:", text)
        self.assertIn("cpu_benchmark_artifact:", text)
        self.assertIn("vector_demo_benchmark_artifact:", text)

    def test_tag_prep_keeps_limits_and_non_goals_visible(self):
        text = TAG_PREP.read_text(encoding="utf-8")

        self.assertIn("No full MIP optimality proof", text)
        self.assertIn("No drop-in replacement for existing solvers", text)
        self.assertIn("No broad performance claim without CUDA timing evidence", text)
        self.assertIn("Full solver compatibility", text)
        self.assertIn("Stable external adapter compatibility", text)

    def test_roadmap_advances_after_phase_25(self):
        text = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("docs/PHASE25_COMPLETION.md", text)
        self.assertIn("Phase 26", text)
        self.assertIn("Phase 27", text)
        self.assertIn("Phase 28", text)
        self.assertIn("Phase 29", text)
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
        self.assertIn("docs/PHASE52_COMPLETION.md", text)
        self.assertIn("Phase 53", text)
        self.assertIn("docs/PHASE53_COMPLETION.md", text)
        self.assertIn("Phase 54", text)
        self.assertIn("docs/PHASE54_COMPLETION.md", text)
        self.assertIn("Phase 55", text)
        self.assertIn("docs/PHASE55_COMPLETION.md", text)
        self.assertIn("Phase 56", text)
        self.assertIn("docs/PHASE56_COMPLETION.md", text)
        self.assertIn("Phase 57", text)
        self.assertIn("The next concrete step is Phase 57", text)


if __name__ == "__main__":
    unittest.main()
