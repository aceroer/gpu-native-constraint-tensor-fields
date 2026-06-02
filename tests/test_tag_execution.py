import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG = "v0.1.0-alpha.0"
TAG_EXECUTION = ROOT / "docs" / "TAG_EXECUTION.md"
RELEASE_NOTES = ROOT / "docs" / "RELEASE_NOTES_DRAFT.md"


class TagExecutionTests(unittest.TestCase):
    def test_tag_execution_doc_names_final_tag_and_artifacts(self):
        text = TAG_EXECUTION.read_text(encoding="utf-8")

        self.assertIn(f"final_tag: {TAG}", text)
        self.assertIn("/tmp/apc-release-artifacts.json", text)
        self.assertIn("/tmp/apc-release-verify-full.json", text)
        self.assertIn("public terminology boundary scan: empty", text)

    def test_release_notes_record_final_tag_and_evidence_paths(self):
        text = RELEASE_NOTES.read_text(encoding="utf-8")

        self.assertIn(f"final_tag: {TAG}", text)
        self.assertIn("tag_target:", text)
        self.assertIn("release_artifact_report: /tmp/apc-release-artifacts.json", text)
        self.assertIn("release_verifier_full_artifact: /tmp/apc-release-verify-full.json", text)

    def test_local_tag_points_to_head(self):
        head = _git(["rev-parse", "HEAD"])
        tag_target = _git(["rev-parse", f"{TAG}^{{commit}}"])

        self.assertEqual(tag_target, head)


def _git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


if __name__ == "__main__":
    unittest.main()
