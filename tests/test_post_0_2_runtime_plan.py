import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "POST_0_2_RUNTIME_PLAN.md"
NEXT_MAJOR_STAGE = ROOT / "docs" / "NEXT_MAJOR_STAGE.md"
ROADMAP = ROOT / "ROADMAP.md"
PUBLIC_HANDOFF = ROOT / "docs" / "PUBLIC_HANDOFF.md"
RELEASE_ARTIFACTS = ROOT / "docs" / "RELEASE_ARTIFACTS.md"


class Post02RuntimePlanTests(unittest.TestCase):
    def test_plan_names_reference_first_runtime_order(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("0.3 Reference-First Runtime Expansion", text)
        self.assertIn("QUBO CPU reference execution", text)
        self.assertIn("additional CPU reference routes", text)
        self.assertIn("broader CUDA parity", text)
        self.assertIn("benchmark sweep expansion", text)
        self.assertIn("problem-family fixture expansion", text)
        self.assertIn("public 0.3 release evidence", text)

    def test_plan_gates_cuda_on_cpu_references(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("No CUDA parity route before the matching CPU reference exists", text)
        self.assertIn("Each CUDA target has a CPU reference test", text)
        self.assertIn("CUDA tests skip cleanly without nvcc or a CUDA device", text)
        self.assertIn("without complete timing evidence", text)

    def test_plan_keeps_public_boundaries_visible(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("No drop-in replacement claim", text)
        self.assertIn("No solver-compatibility promise before a checked adapter exists", text)
        self.assertIn("Fixture docs avoid solver compatibility and performance claims", text)
        self.assertNotIn("compatible with", text)
        self.assertNotIn("speedup", text.lower())

    def test_project_docs_reference_plan_and_next_phase(self):
        next_stage = NEXT_MAJOR_STAGE.read_text(encoding="utf-8")
        roadmap = ROADMAP.read_text(encoding="utf-8")
        handoff = PUBLIC_HANDOFF.read_text(encoding="utf-8")
        artifacts = RELEASE_ARTIFACTS.read_text(encoding="utf-8")

        self.assertIn("docs/POST_0_2_RUNTIME_PLAN.md", next_stage)
        self.assertIn("docs/POST_0_2_RUNTIME_PLAN.md", roadmap)
        self.assertIn("docs/POST_0_2_RUNTIME_PLAN.md", handoff)
        self.assertIn("docs/POST_0_2_RUNTIME_PLAN.md", artifacts)
        self.assertIn("docs/PHASE59_COMPLETION.md", roadmap)
        self.assertIn("Phase 60", roadmap)
        self.assertIn("docs/PHASE60_COMPLETION.md", roadmap)
        self.assertIn("Phase 61", roadmap)
        self.assertIn("docs/PHASE61_COMPLETION.md", roadmap)
        self.assertIn("Phase 62", roadmap)
        self.assertIn("docs/PHASE62_COMPLETION.md", roadmap)
        self.assertIn("Phase 63", roadmap)
        self.assertIn("docs/PHASE63_COMPLETION.md", roadmap)
        self.assertIn("Phase 64", roadmap)
        self.assertIn("docs/PHASE64_COMPLETION.md", roadmap)
        self.assertIn("Phase 65", roadmap)
        self.assertIn("docs/PHASE65_COMPLETION.md", roadmap)
        self.assertIn("Phase 66", roadmap)
        self.assertIn("docs/PHASE66_COMPLETION.md", roadmap)
        self.assertIn("Phase 67", roadmap)
        self.assertIn("docs/PHASE67_COMPLETION.md", roadmap)
        self.assertIn("Phase 68", roadmap)
        self.assertIn("docs/PHASE68_COMPLETION.md", roadmap)
        self.assertIn("Phase 69", roadmap)
        self.assertIn("docs/POST_0_3_RUNTIME_PLAN.md", roadmap)
        self.assertIn("Phase 79", roadmap)
        self.assertIn("docs/PHASE79_COMPLETION.md", roadmap)
        self.assertIn("docs/POST_0_4_BETA_PLAN.md", roadmap)
        self.assertIn("apc.runtime_debug_beta_checkpoint.v1", roadmap)
        self.assertIn("0.4 beta evidence package", roadmap)


if __name__ == "__main__":
    unittest.main()
