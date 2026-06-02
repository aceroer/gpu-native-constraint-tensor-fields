import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CHECKLIST = DOCS / "RELEASE_CHECKLIST.md"
RELEASE_NOTES = DOCS / "RELEASE_NOTES_DRAFT.md"


class ReleaseChecklistTests(unittest.TestCase):
    def test_checklist_references_release_verifier(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/verify_public_release.py", text)
        self.assertIn("--full", text)
        self.assertIn("apc.public_release_verification.v1", text)

    def test_checklist_names_tag_docs_tests_and_benchmarks(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        self.assertIn("v0.1.0-alpha.N", text)
        self.assertIn("README.md", text)
        self.assertIn("ROADMAP.md", text)
        self.assertIn("docs/QUICKSTART.md", text)
        self.assertIn("python3 -m unittest discover -s tests -v", text)
        self.assertIn("/tmp/apc-release-bench.json", text)
        self.assertIn("/tmp/apc-release-vector-demo-bench.json", text)
        self.assertIn("payload.benchmark.schema apc.vector_demo_benchmark.v1", text)

    def test_release_notes_include_release_readiness_surface(self):
        text = RELEASE_NOTES.read_text(encoding="utf-8")

        self.assertIn("release verifier", text)
        self.assertIn("release checklist", text)
        self.assertIn("apc.public_release_verification.v1", text)
        self.assertIn("Small release tag", text)

    def test_checklist_vector_benchmark_schema_matches_script_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "vector_demo_bench.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_vector_demo_bench.py",
                    "examples/specs/binary_milp_tiny.json",
                    "--out",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(
            report["payload"]["benchmark"]["schema"],
            "apc.vector_demo_benchmark.v1",
        )


if __name__ == "__main__":
    unittest.main()
