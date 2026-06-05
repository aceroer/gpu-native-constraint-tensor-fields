import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HANDOFF = DOCS / "PUBLIC_HANDOFF.md"
RELEASE_NOTES = DOCS / "RELEASE_NOTES_DRAFT.md"
NEXT_MAJOR_STAGE = DOCS / "NEXT_MAJOR_STAGE.md"
ROADMAP = ROOT / "ROADMAP.md"


class PublicDocsTests(unittest.TestCase):
    def test_handoff_names_stable_entry_points_and_extensions(self):
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("docs/QUICKSTART.md", text)
        self.assertIn("src/apc/state_pool.py", text)
        self.assertIn("src/apc/branch_tensor.py", text)
        self.assertIn("src/apc/reduction_gate.py", text)
        self.assertIn("Extension Areas", text)
        self.assertIn("src/apc/runtime_contract.py", text)
        self.assertIn("src/apc/operator_call_ledger.py", text)
        self.assertIn("src/apc/runtime_status.py", text)
        self.assertIn("src/apc/readings/maxsat.py", text)
        self.assertIn("src/apc/readings/qubo.py", text)
        self.assertIn("native/include/apc_runtime.hpp", text)
        self.assertIn("native/src/cpu_operator_shim.cpp", text)
        self.assertIn("docs/CUDA_OPERATOR_PARITY.md", text)
        self.assertIn("docs/BENCHMARK_SWEEPS.md", text)
        self.assertIn("docs/PROBLEM_FAMILIES.md", text)
        self.assertIn("docs/RELEASE_CHECKLIST_0_2.md", text)
        self.assertIn("docs/RELEASE_NOTES_0_2_DRAFT.md", text)
        self.assertIn("docs/RELEASE_ARCHIVE_0_2.md", text)
        self.assertIn("docs/TAG_EXECUTION_0_2.md", text)
        self.assertIn("examples/handoff/problem_family_fixtures.v1.json", text)
        self.assertIn("python3 scripts/run_benchmark_sweep.py", text)
        self.assertIn("python3 scripts/inspect_benchmark_sweep.py", text)
        self.assertIn("python3 scripts/list_problem_family_fixtures.py", text)
        self.assertIn("Add a new small native problem spec", text)
        self.assertIn("Add a runtime contract step", text)
        self.assertIn("Add an operator call ledger row", text)
        self.assertIn("Add a runtime status code", text)
        self.assertIn("Add a native host ABI field", text)
        self.assertIn("Add a native CPU shim probe", text)
        self.assertIn("python3 scripts/probe_native_host.py", text)
        self.assertIn("Add a CUDA parity target", text)
        self.assertIn("Add a benchmark sweep config", text)
        self.assertIn("Add a benchmark sweep runner check", text)
        self.assertIn("Add a benchmark sweep reader check", text)
        self.assertIn("Add a problem-family runtime route", text)
        self.assertIn("Add a problem-family lowering route", text)
        self.assertIn("Add a problem-family fixture record", text)
        self.assertIn("Add a problem-family lowering route", text)

    def test_release_notes_summarize_public_phases(self):
        text = RELEASE_NOTES.read_text(encoding="utf-8")

        self.assertIn("CTIR lowering", text)
        self.assertIn("CPU reference repair runtime", text)
        self.assertIn("Benchmark harness", text)
        self.assertIn("StatePool, BranchTensor, ReductionGate, and InterfaceProjection", text)
        self.assertIn("Vector-native repair demo", text)

    def test_next_major_stage_names_solo_buildout_route(self):
        roadmap = ROADMAP.read_text(encoding="utf-8")
        text = NEXT_MAJOR_STAGE.read_text(encoding="utf-8")

        self.assertIn("docs/NEXT_MAJOR_STAGE.md", roadmap)
        self.assertIn("0.2 Native Runtime Buildout", text)
        self.assertIn("Runtime Execution Contract", text)
        self.assertIn("C++ Host Runtime Skeleton", text)
        self.assertIn("CUDA Operator Parity", text)
        self.assertIn("Benchmark Sweeps", text)
        self.assertIn("Problem-Family Expansion", text)
        self.assertIn("Every CUDA path has a CPU reference", text)

    def test_public_docs_pass_terminology_boundary(self):
        forbidden = (
            "INTER" + "NAL",
            "internal" + "_layers",
            "Local" + "/private",
            "场" + "代数",
            "Max" + "well",
            "电路" + "模块",
            "母" + "理论",
            "内部" + "组装",
            "成熟" + "读数",
        )
        public_docs = [
            path
            for path in DOCS.glob("*.md")
            if not path.name.startswith("PHASE") and not path.name.startswith("._")
        ]

        for path in public_docs:
            text = path.read_text(encoding="utf-8")
            for term in forbidden:
                self.assertNotIn(term, text, f"{term} leaked in {path}")


if __name__ == "__main__":
    unittest.main()
