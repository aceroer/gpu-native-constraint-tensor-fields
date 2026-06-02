import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUICKSTART = ROOT / "docs" / "QUICKSTART.md"


class QuickstartTests(unittest.TestCase):
    def test_quickstart_commands_are_copy_paste_runnable_from_root(self):
        env = os.environ.copy()
        with tempfile.TemporaryDirectory() as tmpdir:
            replacements = {
                "/tmp/apc-ledger.json": str(Path(tmpdir) / "apc-ledger.json"),
                "/tmp/apc-bench.json": str(Path(tmpdir) / "apc-bench.json"),
                "/tmp/apc-vector-demo.json": str(Path(tmpdir) / "apc-vector-demo.json"),
                "/tmp/apc-vector-demo-bench.json": str(Path(tmpdir) / "apc-vector-demo-bench.json"),
                "/tmp/apc-cuda-bench.json": str(Path(tmpdir) / "apc-cuda-bench.json"),
            }
            for command in _quickstart_commands():
                rewritten = command
                for source, target in replacements.items():
                    rewritten = rewritten.replace(source, target)
                completed = subprocess.run(
                    rewritten,
                    cwd=ROOT,
                    shell=True,
                    text=True,
                    capture_output=True,
                    env=env,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)

            bench = json.loads(Path(replacements["/tmp/apc-bench.json"]).read_text(encoding="utf-8"))
            vector_bench = json.loads(
                Path(replacements["/tmp/apc-vector-demo-bench.json"]).read_text(encoding="utf-8")
            )

        self.assertEqual(bench["schema"], "apc.benchmark.v1")
        self.assertEqual(vector_bench["projection"]["kind"], "runtime_summary")
        self.assertIn("benchmark", vector_bench["payload"])

    def test_quickstart_covers_required_first_run_commands(self):
        text = QUICKSTART.read_text(encoding="utf-8")

        self.assertIn("apc.cli validate", text)
        self.assertIn("apc.cli run", text)
        self.assertIn("scripts/run_bench.py", text)
        self.assertIn("scripts/run_vector_demo_bench.py", text)

    def test_public_quickstart_has_no_internal_only_terms(self):
        text = QUICKSTART.read_text(encoding="utf-8")
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

        for term in forbidden:
            self.assertNotIn(term, text)


def _quickstart_commands() -> list[str]:
    text = QUICKSTART.read_text(encoding="utf-8")
    commands: list[str] = []
    for block in re.findall(r"```bash\n(.*?)\n```", text, flags=re.DOTALL):
        commands.extend(line.strip() for line in block.splitlines() if line.strip())
    return commands


if __name__ == "__main__":
    unittest.main()
