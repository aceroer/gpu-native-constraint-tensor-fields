import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.collect_release_artifacts import collect_release_artifacts


ROOT = Path(__file__).resolve().parents[1]


class ReleaseArtifactTests(unittest.TestCase):
    def test_collector_emits_json_ready_release_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verify = tmp / "verify.json"
            bench = tmp / "bench.json"
            vector = tmp / "vector.json"
            handoff = tmp / "handoff-fixtures.json"
            qubo = tmp / "qubo-runtime.json"
            out = tmp / "artifacts.json"
            _write_fixture_artifacts(
                verify=verify,
                bench=bench,
                vector=vector,
                handoff=handoff,
                qubo=qubo,
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/collect_release_artifacts.py",
                    "--tag",
                    "v0.1.0-test",
                    "--verify",
                    str(verify),
                    "--bench",
                    str(bench),
                    "--vector-bench",
                    str(vector),
                    "--handoff-fixtures",
                    str(handoff),
                    "--qubo-runtime",
                    str(qubo),
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            stdout_report = json.loads(completed.stdout)
            file_report = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(stdout_report["schema"], "apc.release_artifacts.v1")
        self.assertEqual(file_report["status"], "ok")
        self.assertEqual(file_report["tag"], "v0.1.0-test")
        self.assertEqual(len(file_report["commit"]), 40)
        self.assertIn("verifier", file_report["artifacts"])
        self.assertIn("cpu_benchmark", file_report["artifacts"])
        self.assertIn("vector_demo_benchmark", file_report["artifacts"])
        self.assertIn("handoff_fixture_listing", file_report["artifacts"])
        self.assertIn("qubo_runtime", file_report["artifacts"])
        self.assertEqual(
            file_report["artifacts"]["handoff_fixture_listing"]["schema"],
            "apc.handoff_fixture_index.v1",
        )
        self.assertEqual(
            file_report["artifacts"]["qubo_runtime"]["schema"],
            "apc.qubo_cpu_reference_execution.v1",
        )
        self.assertIn("examples", file_report)
        self.assertIn("docs/TAG_PREP.md", [item["path"] for item in file_report["docs"]])
        self.assertIn("docs/TAG_EXECUTION.md", [item["path"] for item in file_report["docs"]])
        self.assertIn("docs/POST_0_2_RUNTIME_PLAN.md", [item["path"] for item in file_report["docs"]])
        self.assertIn("docs/RELEASE_ARCHIVE.md", [item["path"] for item in file_report["docs"]])
        self.assertIn("docs/CROSS_PROJECT_HANDOFF.md", [item["path"] for item in file_report["docs"]])
        self.assertIn("docs/CHECKED_HANDOFF_DEMO.md", [item["path"] for item in file_report["docs"]])
        self.assertIn("tests/test_tag_prep.py", [item["path"] for item in file_report["tests"]])
        self.assertIn("tests/test_tag_execution.py", [item["path"] for item in file_report["tests"]])
        self.assertIn("tests/test_post_0_2_runtime_plan.py", [item["path"] for item in file_report["tests"]])
        self.assertIn("tests/test_release_archive.py", [item["path"] for item in file_report["tests"]])
        self.assertIn("tests/test_cross_project_handoff.py", [item["path"] for item in file_report["tests"]])
        self.assertIn("tests/test_checked_handoff_demo.py", [item["path"] for item in file_report["tests"]])
        self.assertIn("tests/test_checked_handoff_fixtures.py", [item["path"] for item in file_report["tests"]])
        self.assertIn(
            "tests/test_problem_family_handoff_fixture.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_handoff_fixture_index.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_handoff_fixture_listing.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_release_artifact_reader.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_release_evidence_smoke.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_maintenance_releases.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_runtime_contract.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_operator_call_ledger.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_runtime_status.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_native_host_abi.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_native_cpu_operator_shim.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_native_binding_probe.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/cuda/test_cuda_arch_config.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/cuda/test_linear_csr_eval.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/cuda/test_projection.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/cuda/test_penalty_reduce.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/cuda/test_clause_eval.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/cuda/test_parity_target_selection.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/cuda/test_qubo_energy.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_benchmark_sweep.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_benchmark_sweep_runner.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_benchmark_sweep_report.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_maxsat_runtime_route.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_qubo_spec_lowering.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_qubo_cpu_reference_contract.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_qubo_cpu_reference.py",
            [item["path"] for item in file_report["tests"]],
        )
        self.assertIn(
            "tests/test_problem_family_fixture_set.py",
            [item["path"] for item in file_report["tests"]],
        )
        example_schemas = {item["path"]: item["schema"] for item in file_report["examples"]}
        self.assertIn("examples/handoff/README.md", example_schemas)
        self.assertEqual(
            example_schemas["examples/handoff/problem_family_fixtures.v1.json"],
            "apc.problem_family_fixture_index.v1",
        )
        self.assertEqual(
            example_schemas["examples/handoff/vagent_apc_handoff_report.v1.json"],
            "vagent.apc_handoff_report.v1",
        )
        self.assertEqual(
            example_schemas["examples/handoff/apc_handoff_check.v1.json"],
            "apc.cross_project_handoff_check.v1",
        )
        self.assertEqual(
            example_schemas["examples/handoff/apc_checked_handoff_demo.v1.json"],
            "apc.checked_handoff_runtime_demo.v1",
        )
        self.assertEqual(
            example_schemas["examples/handoff/vagent_binary_milp_handoff_report.v1.json"],
            "vagent.apc_handoff_report.v1",
        )
        self.assertEqual(
            example_schemas["examples/handoff/apc_binary_milp_handoff_check.v1.json"],
            "apc.cross_project_handoff_check.v1",
        )
        self.assertEqual(
            example_schemas["examples/handoff/apc_binary_milp_checked_handoff_demo.v1.json"],
            "apc.checked_handoff_runtime_demo.v1",
        )
        self.assertIn(
            "handoff_fixture_schemas",
            [item["name"] for item in file_report["checks"]],
        )

    def test_collector_marks_missing_artifact_failed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verify = tmp / "verify.json"
            bench = tmp / "bench.json"
            vector = tmp / "missing-vector.json"
            handoff = tmp / "handoff-fixtures.json"
            qubo = tmp / "qubo-runtime.json"
            _write_fixture_artifacts(
                verify=verify,
                bench=bench,
                vector=tmp / "unused.json",
                handoff=handoff,
                qubo=qubo,
            )
            vector.unlink(missing_ok=True)

            report = collect_release_artifacts(
                tag="v0.1.0-test",
                verify_path=verify,
                bench_path=bench,
                vector_bench_path=vector,
                handoff_fixtures_path=handoff,
                qubo_runtime_path=qubo,
            )

        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["artifacts"]["vector_demo_benchmark"]["exists"])

    def test_collector_marks_missing_handoff_listing_failed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verify = tmp / "verify.json"
            bench = tmp / "bench.json"
            vector = tmp / "vector.json"
            handoff = tmp / "missing-handoff-fixtures.json"
            qubo = tmp / "qubo-runtime.json"
            _write_fixture_artifacts(
                verify=verify,
                bench=bench,
                vector=vector,
                handoff=tmp / "unused-handoff.json",
                qubo=qubo,
            )
            handoff.unlink(missing_ok=True)

            report = collect_release_artifacts(
                tag="v0.1.0-test",
                verify_path=verify,
                bench_path=bench,
                vector_bench_path=vector,
                handoff_fixtures_path=handoff,
                qubo_runtime_path=qubo,
            )

        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["artifacts"]["handoff_fixture_listing"]["exists"])

    def test_release_artifacts_doc_names_contract(self):
        text = (ROOT / "docs" / "RELEASE_ARTIFACTS.md").read_text(encoding="utf-8")
        notes = (ROOT / "docs" / "RELEASE_NOTES_DRAFT.md").read_text(encoding="utf-8")

        self.assertIn("apc.release_artifacts.v1", text)
        self.assertIn("apc.release_artifacts_summary.v1", text)
        self.assertIn("apc.release_evidence_smoke.v1", text)
        self.assertIn("commit", text)
        self.assertIn("scripts/collect_release_artifacts.py", text)
        self.assertIn("scripts/inspect_release_artifacts.py", text)
        self.assertIn("scripts/smoke_release_evidence.py", text)
        self.assertIn("docs/MAINTENANCE_RELEASES.md", text)
        self.assertIn("docs/RELEASE_CHECKLIST_0_2.md", text)
        self.assertIn("docs/RELEASE_CHECKLIST_0_3.md", text)
        self.assertIn("docs/RELEASE_NOTES_0_2_DRAFT.md", text)
        self.assertIn("docs/RELEASE_NOTES_0_3_DRAFT.md", text)
        self.assertIn("docs/RELEASE_ARCHIVE_0_2.md", text)
        self.assertIn("docs/RELEASE_ARCHIVE_0_3.md", text)
        self.assertIn("docs/TAG_EXECUTION_0_2.md", text)
        self.assertIn("docs/TAG_EXECUTION_0_3.md", text)
        self.assertIn("docs/RUNTIME_CONTRACT.md", text)
        self.assertIn("tests/test_release_checklist_0_2.py", text)
        self.assertIn("tests/test_release_checklist_0_3.py", text)
        self.assertIn("tests/test_release_artifacts_0_2.py", text)
        self.assertIn("tests/test_tag_execution_0_2.py", text)
        self.assertIn("tests/test_maintenance_releases.py", text)
        self.assertIn("tests/test_runtime_contract.py", text)
        self.assertIn("tests/test_operator_call_ledger.py", text)
        self.assertIn("tests/test_runtime_status.py", text)
        self.assertIn("tests/test_native_host_abi.py", text)
        self.assertIn("tests/test_native_cpu_operator_shim.py", text)
        self.assertIn("tests/test_native_binding_probe.py", text)
        self.assertIn("docs/CUDA_OPERATOR_PARITY.md", text)
        self.assertIn("tests/cuda/test_linear_csr_eval.py", text)
        self.assertIn("tests/cuda/test_projection.py", text)
        self.assertIn("tests/cuda/test_penalty_reduce.py", text)
        self.assertIn("tests/cuda/test_clause_eval.py", text)
        self.assertIn("tests/cuda/test_parity_target_selection.py", text)
        self.assertIn("tests/cuda/test_qubo_energy.py", text)
        self.assertIn("docs/BENCHMARK_SWEEPS.md", text)
        self.assertIn("benchmarks/sweeps/binary_milp_smoke.json", text)
        self.assertIn("benchmarks/sweeps/qubo_smoke.json", text)
        self.assertIn("benchmarks/sweeps/maxsat_smoke.json", text)
        self.assertIn("scripts/run_benchmark_sweep.py", text)
        self.assertIn("scripts/inspect_benchmark_sweep.py", text)
        self.assertIn("tests/test_benchmark_sweep.py", text)
        self.assertIn("tests/test_benchmark_sweep_runner.py", text)
        self.assertIn("tests/test_benchmark_sweep_report.py", text)
        self.assertIn("src/apc/readings/maxsat.py", text)
        self.assertIn("examples/specs/maxsat_tiny.json", text)
        self.assertIn("docs/PROBLEM_FAMILIES.md", text)
        self.assertIn("tests/test_maxsat_runtime_route.py", text)
        self.assertIn("src/apc/readings/qubo.py", text)
        self.assertIn("examples/specs/qubo_tiny.json", text)
        self.assertIn("tests/test_qubo_spec_lowering.py", text)
        self.assertIn("tests/test_qubo_cpu_reference.py", text)
        self.assertIn("apc.qubo_cpu_reference_execution.v1", text)
        self.assertIn("scripts/list_problem_family_fixtures.py", text)
        self.assertIn("examples/handoff/problem_family_fixtures.v1.json", text)
        self.assertIn("tests/test_problem_family_fixture_set.py", text)
        self.assertIn("release artifact contract", notes)


def _write_fixture_artifacts(
    *,
    verify: Path,
    bench: Path,
    vector: Path,
    handoff: Path,
    qubo: Path,
) -> None:
    verify.write_text(
        json.dumps(
            {
                "schema": "apc.public_release_verification.v1",
                "status": "ok",
                "mode": "quick",
                "checks": [],
            }
        ),
        encoding="utf-8",
    )
    bench.write_text(
        json.dumps(
            {
                "schema": "apc.benchmark.v1",
                "metrics": {},
                "notes": [],
            }
        ),
        encoding="utf-8",
    )
    vector.write_text(
        json.dumps(
            {
                "payload": {
                    "benchmark": {
                        "schema": "apc.vector_demo_benchmark.v1",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    handoff.write_text(
        json.dumps(
            {
                "schema": "apc.handoff_fixture_index.v1",
                "status": "ok",
                "fixture_count": 2,
                "fixtures": [],
            }
        ),
        encoding="utf-8",
    )
    qubo.write_text(
        json.dumps(
            {
                "schema": "apc.qubo_cpu_reference_execution.v1",
                "status": "implemented",
                "backend": "cpu",
                "problem_family": "qubo",
                "ledger": [],
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
