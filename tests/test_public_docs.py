import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HANDOFF = DOCS / "PUBLIC_HANDOFF.md"
RELEASE_NOTES = DOCS / "RELEASE_NOTES_DRAFT.md"


class PublicDocsTests(unittest.TestCase):
    def test_handoff_names_stable_entry_points_and_extensions(self):
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("docs/QUICKSTART.md", text)
        self.assertIn("src/apc/state_pool.py", text)
        self.assertIn("src/apc/branch_tensor.py", text)
        self.assertIn("src/apc/reduction_gate.py", text)
        self.assertIn("Extension Areas", text)
        self.assertIn("Add a new small native problem spec", text)

    def test_release_notes_summarize_public_phases(self):
        text = RELEASE_NOTES.read_text(encoding="utf-8")

        self.assertIn("CTIR lowering", text)
        self.assertIn("CPU reference repair runtime", text)
        self.assertIn("Benchmark harness", text)
        self.assertIn("StatePool, BranchTensor, ReductionGate, and InterfaceProjection", text)
        self.assertIn("Vector-native repair demo", text)

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
            if not path.name.startswith("PHASE")
        ]

        for path in public_docs:
            text = path.read_text(encoding="utf-8")
            for term in forbidden:
                self.assertNotIn(term, text, f"{term} leaked in {path}")


if __name__ == "__main__":
    unittest.main()
