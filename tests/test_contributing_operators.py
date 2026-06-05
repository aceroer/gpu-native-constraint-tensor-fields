import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "CONTRIBUTING_OPERATORS.md"
PUBLIC_HANDOFF = ROOT / "docs" / "PUBLIC_HANDOFF.md"
RELEASE_ARTIFACTS = ROOT / "docs" / "RELEASE_ARTIFACTS.md"


class ContributingOperatorsTests(unittest.TestCase):
    def test_guide_names_public_extension_order(self):
        text = GUIDE.read_text(encoding="utf-8")

        self.assertIn("spec", text)
        self.assertIn("lowering", text)
        self.assertIn("CPU reference", text)
        self.assertIn("tests", text)
        self.assertIn("optional CUDA parity", text)
        self.assertIn("release evidence", text)

    def test_guide_names_required_docs_fixtures_and_evidence(self):
        text = GUIDE.read_text(encoding="utf-8")

        self.assertIn("examples/handoff/problem_family_fixtures.v1.json", text)
        self.assertIn("docs/PROBLEM_FAMILIES.md", text)
        self.assertIn("docs/RUNTIME_CONTRACT.md", text)
        self.assertIn("docs/CUDA_OPERATOR_PARITY.md", text)
        self.assertIn("docs/BENCHMARK_SWEEPS.md", text)
        self.assertIn("scripts/collect_release_artifacts.py", text)
        self.assertIn("run artifact directory", text)
        self.assertIn("CUDA parity report", text)

    def test_guide_keeps_claim_boundaries_visible(self):
        text = GUIDE.read_text(encoding="utf-8")

        self.assertIn("Do not add", text)
        self.assertIn("drop-in replacement claims", text)
        self.assertIn("solver compatibility promises before a checked adapter exists", text)
        self.assertIn("performance claims without complete timing evidence", text)
        self.assertNotIn("speedup", text.lower())

    def test_public_docs_reference_guide(self):
        handoff = PUBLIC_HANDOFF.read_text(encoding="utf-8")
        artifacts = RELEASE_ARTIFACTS.read_text(encoding="utf-8")

        self.assertIn("docs/CONTRIBUTING_OPERATORS.md", handoff)
        self.assertIn("docs/CONTRIBUTING_OPERATORS.md", artifacts)
        self.assertIn("tests/test_contributing_operators.py", artifacts)


if __name__ == "__main__":
    unittest.main()
