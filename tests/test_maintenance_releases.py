import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "MAINTENANCE_RELEASES.md"
ROADMAP = ROOT / "ROADMAP.md"
RELEASE_ARTIFACTS = ROOT / "docs" / "RELEASE_ARTIFACTS.md"


class MaintenanceReleaseTests(unittest.TestCase):
    def test_maintenance_procedure_references_smoke_command(self):
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/smoke_release_evidence.py", text)
        self.assertIn("--tag <candidate_patch_tag>", text)
        self.assertIn("/tmp/apc-release-evidence-smoke.json", text)
        self.assertIn("apc.release_evidence_smoke.v1", text)

    def test_maintenance_procedure_names_patch_inputs_and_outputs(self):
        text = DOC.read_text(encoding="utf-8")

        for field in (
            "candidate_patch_tag",
            "intended_commit",
            "base_tag",
            "release_evidence_smoke_report",
            "release_artifact_report",
            "release_artifact_summary",
        ):
            self.assertIn(field, text)
        self.assertIn("release artifact summary commit: intended_commit", text)
        self.assertIn("release artifact summary tag: candidate_patch_tag", text)
        self.assertIn("failed checks: []", text)

    def test_maintenance_procedure_keeps_limits_factual(self):
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("Refusal Conditions", text)
        self.assertIn("Scope Limits", text)
        self.assertIn("does not change the project limits", text)
        self.assertIn("should not include", text)
        self.assertNotIn("drop-in", text.lower())
        self.assertNotIn("speedup", text.lower())

    def test_release_artifacts_and_roadmap_include_maintenance_route(self):
        roadmap = ROADMAP.read_text(encoding="utf-8")
        artifacts = RELEASE_ARTIFACTS.read_text(encoding="utf-8")

        self.assertIn("docs/MAINTENANCE_RELEASES.md", roadmap)
        self.assertIn("docs/PHASE39_COMPLETION.md", roadmap)
        self.assertIn("Phase 50", roadmap)
        self.assertIn("docs/PHASE50_COMPLETION.md", roadmap)
        self.assertIn("Phase 51", roadmap)
        self.assertIn("docs/PHASE51_COMPLETION.md", roadmap)
        self.assertIn("Phase 52", roadmap)
        self.assertIn("docs/PHASE52_COMPLETION.md", roadmap)
        self.assertIn("Phase 53", roadmap)
        self.assertIn("docs/PHASE53_COMPLETION.md", roadmap)
        self.assertIn("Phase 54", roadmap)
        self.assertIn("docs/PHASE54_COMPLETION.md", roadmap)
        self.assertIn("Phase 55", roadmap)
        self.assertIn("docs/PHASE55_COMPLETION.md", roadmap)
        self.assertIn("Phase 56", roadmap)
        self.assertIn("docs/MAINTENANCE_RELEASES.md", artifacts)
        self.assertIn("tests/test_maintenance_releases.py", artifacts)


if __name__ == "__main__":
    unittest.main()
