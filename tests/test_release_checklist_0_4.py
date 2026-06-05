import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs" / "RELEASE_CHECKLIST_0_4.md"
NOTES = ROOT / "docs" / "RELEASE_NOTES_0_4_DRAFT.md"
TAG_EXECUTION = ROOT / "docs" / "TAG_EXECUTION_0_4.md"


class ReleaseChecklist04Tests(unittest.TestCase):
    def test_checklist_names_0_4_gates(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        self.assertIn("0.4 is the Native Runtime Consolidation release candidate", text)
        self.assertIn("QUBO CUDA move scoring parity", text)
        self.assertIn("CUDA parity report", text)
        self.assertIn("runtime CLI family routing", text)
        self.assertIn("run artifact writer", text)
        self.assertIn("runtime debug report", text)

    def test_checklist_names_required_commands_and_schemas(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        self.assertIn("scripts/verify_public_release.py --full", text)
        self.assertIn("scripts/inspect_cuda_parity.py", text)
        self.assertIn("scripts/inspect_runtime_debug.py", text)
        self.assertIn("--verify /tmp/apc-release-verify-full-0-4.json", text)
        self.assertIn("--release-artifacts /tmp/apc-release-artifacts-0-4.json", text)
        self.assertIn("scripts/run_benchmark_sweep.py benchmarks/sweeps/qubo_smoke.json", text)
        self.assertIn("apc.cuda_parity_report.v1", text)
        self.assertIn("apc.run_artifacts.v1", text)
        self.assertIn("apc.runtime_debug_report.v1", text)
        self.assertIn("apc.runtime_debug_beta_checkpoint.v1", text)

    def test_notes_and_tag_execution_keep_limits_visible(self):
        notes = NOTES.read_text(encoding="utf-8")
        tag = TAG_EXECUTION.read_text(encoding="utf-8")

        self.assertIn("v0.4.0-alpha.N", notes)
        self.assertIn("does not claim solver API compatibility", notes)
        self.assertIn("does not claim", tag)
        self.assertIn("No performance claim", tag)
        self.assertNotIn("speedup", (notes + tag).lower())


if __name__ == "__main__":
    unittest.main()
