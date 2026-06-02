import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs" / "RELEASE_ARCHIVE.md"
RELEASE_NOTES = ROOT / "docs" / "RELEASE_NOTES_DRAFT.md"
ROADMAP = ROOT / "ROADMAP.md"
TAG = "v0.1.0-alpha.0"
TAG_COMMIT = "b051c20b38ff19cf99992daa72dc1e9558ec7b84"


class ReleaseArchiveTests(unittest.TestCase):
    def test_archive_names_tag_and_evidence_artifacts(self):
        text = ARCHIVE.read_text(encoding="utf-8")

        self.assertIn(f"tag: {TAG}", text)
        self.assertIn(f"tag_commit: {TAG_COMMIT}", text)
        self.assertIn("/tmp/apc-release-verify-full.json", text)
        self.assertIn("/tmp/apc-release-artifacts.json", text)
        self.assertIn("apc.release_artifacts.v1", text)
        self.assertIn("apc.vector_demo_benchmark.v1", text)

    def test_archive_records_reproduction_commands(self):
        text = ARCHIVE.read_text(encoding="utf-8")

        self.assertIn("git fetch --tags origin", text)
        self.assertIn(f"git checkout {TAG}", text)
        self.assertIn("python3 scripts/verify_public_release.py --full", text)
        self.assertIn("python3 scripts/collect_release_artifacts.py", text)
        self.assertIn("public terminology boundary scan: empty", text)

    def test_release_notes_keep_limits_and_next_work_visible(self):
        text = RELEASE_NOTES.read_text(encoding="utf-8")

        self.assertIn(f"archived_tag: {TAG}", text)
        self.assertIn(f"archived_tag_commit: {TAG_COMMIT}", text)
        self.assertIn("No full MIP optimality proof", text)
        self.assertIn("Release archive handoff", text)

    def test_tag_commit_is_still_available_locally(self):
        tag_commit = _git(["rev-parse", f"{TAG}^{{commit}}"])

        self.assertEqual(tag_commit, TAG_COMMIT)

    def test_roadmap_advances_after_phase_27(self):
        text = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("docs/PHASE27_COMPLETION.md", text)
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
        self.assertIn("The next concrete step is Phase 56", text)


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
