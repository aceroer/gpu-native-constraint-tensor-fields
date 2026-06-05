import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "POST_0_3_RUNTIME_PLAN.md"
NEXT_MAJOR_STAGE = ROOT / "docs" / "NEXT_MAJOR_STAGE.md"
ROADMAP = ROOT / "ROADMAP.md"
PUBLIC_HANDOFF = ROOT / "docs" / "PUBLIC_HANDOFF.md"
RELEASE_ARTIFACTS = ROOT / "docs" / "RELEASE_ARTIFACTS.md"


class Post03RuntimePlanTests(unittest.TestCase):
    def test_plan_names_native_runtime_consolidation_order(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("0.4 Native Runtime Consolidation", text)
        self.assertIn("QUBO CUDA move scoring parity", text)
        self.assertIn("CUDA parity report integration", text)
        self.assertIn("runtime CLI family routing", text)
        self.assertIn("run artifact writer", text)
        self.assertIn("native host bridge consolidation", text)
        self.assertIn("benchmark timing expansion", text)
        self.assertIn("contributor extension guide", text)
        self.assertIn("runtime debug tools", text)
        self.assertIn("public 0.4 release evidence", text)

    def test_plan_keeps_cuda_gated_by_cpu_references(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("No CUDA parity route before the matching CPU reference exists", text)
        self.assertIn("Each CUDA target has a CPU reference test", text)
        self.assertIn("CUDA tests skip cleanly without nvcc or a CUDA device", text)
        self.assertIn("without complete timing evidence", text)

    def test_plan_keeps_public_claim_boundaries_visible(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("No drop-in replacement claim", text)
        self.assertIn("No solver-compatibility promise", text)
        self.assertIn("Public docs avoid private research-system terms", text)
        self.assertIn("Every version after 0.4 keeps a debug-tooling checkpoint", text)
        self.assertNotIn("speedup", text.lower())
        self.assertNotIn("compatible with", text)

    def test_plan_adds_debug_tools_for_real_environment_failures(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("Runtime Debug Tools", text)
        self.assertIn("specs, lowered CTIR, layout summaries, ledgers, run artifacts, and status codes", text)
        self.assertIn("device availability, nvcc availability, selected arch, and skip reason", text)
        self.assertIn("Failure records include enough context to reproduce tiny fixture failures", text)

    def test_project_docs_reference_plan_and_next_phase(self):
        next_stage = NEXT_MAJOR_STAGE.read_text(encoding="utf-8")
        roadmap = ROADMAP.read_text(encoding="utf-8")
        handoff = PUBLIC_HANDOFF.read_text(encoding="utf-8")
        artifacts = RELEASE_ARTIFACTS.read_text(encoding="utf-8")

        self.assertIn("docs/POST_0_3_RUNTIME_PLAN.md", next_stage)
        self.assertIn("docs/POST_0_3_RUNTIME_PLAN.md", roadmap)
        self.assertIn("docs/POST_0_3_RUNTIME_PLAN.md", handoff)
        self.assertIn("docs/POST_0_3_RUNTIME_PLAN.md", artifacts)
        self.assertIn("Phase 69", roadmap)
        self.assertIn("docs/PHASE69_COMPLETION.md", roadmap)
        self.assertIn("Phase 70", roadmap)
        self.assertIn("docs/PHASE70_COMPLETION.md", roadmap)
        self.assertIn("Phase 71", roadmap)
        self.assertIn("docs/PHASE71_COMPLETION.md", roadmap)
        self.assertIn("Phase 72", roadmap)
        self.assertIn("docs/PHASE72_COMPLETION.md", roadmap)
        self.assertIn("Phase 73", roadmap)
        self.assertIn("docs/PHASE73_COMPLETION.md", roadmap)
        self.assertIn("Phase 74", roadmap)
        self.assertIn("docs/PHASE74_COMPLETION.md", roadmap)
        self.assertIn("Phase 75", roadmap)
        self.assertIn("docs/PHASE75_COMPLETION.md", roadmap)
        self.assertIn("Phase 76", roadmap)
        self.assertIn("docs/PHASE76_COMPLETION.md", roadmap)
        self.assertIn("Phase 77", roadmap)
        self.assertIn("docs/PHASE77_COMPLETION.md", roadmap)
        self.assertIn("Phase 78", roadmap)
        self.assertIn("docs/PHASE78_COMPLETION.md", roadmap)
        self.assertIn("Phase 79", roadmap)
        self.assertIn("docs/PHASE79_COMPLETION.md", roadmap)
        self.assertIn("QUBO CUDA move scoring parity", roadmap)
        self.assertIn("debug-tooling checkpoint", roadmap)
        self.assertIn("docs/POST_0_4_BETA_PLAN.md", roadmap)
        self.assertIn("apc.runtime_debug_beta_checkpoint.v1", roadmap)
        self.assertIn("0.4 beta evidence package", roadmap)


if __name__ == "__main__":
    unittest.main()
