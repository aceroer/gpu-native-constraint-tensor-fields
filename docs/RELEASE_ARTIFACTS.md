# Release Artifacts

Release artifact normalization collects tag evidence into one JSON-ready report.

## Collector

Run the release verifier first:

```bash
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
```

Then collect release evidence:

```bash
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.N --out /tmp/apc-release-artifacts.json
```

Then inspect the collected evidence:

```bash
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts.json
```

Or run the evidence route as one smoke command:

```bash
python3 scripts/smoke_release_evidence.py --tag v0.1.0-alpha.N --out /tmp/apc-release-evidence-smoke.json
```

The collector reads:

```text
/tmp/apc-release-verify.json
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-handoff-fixtures.json
```

The verifier creates the benchmark artifacts during quick and full runs.

## Schema

The collector emits:

```text
schema: apc.release_artifacts.v1
status
tag
commit
artifacts
docs
tests
examples
checks
```

## Required Evidence

The artifact contract records:

```text
release verifier schema and status
CPU benchmark schema
vector-native demo benchmark schema
handoff fixture listing schema and status
release docs
release tests
maintenance release procedure
runtime execution contract
operator call ledger tests
runtime status code tests
native host ABI header tests
native CPU operator shim tests
native host probe tests
CUDA operator parity docs
benchmark sweep config docs
post-0.2 runtime expansion plan
checked handoff fixture examples
current commit hash
```

Required schemas:

```text
apc.public_release_verification.v1
apc.benchmark.v1
apc.vector_demo_benchmark.v1
apc.handoff_fixture_index.v1
vagent.apc_handoff_report.v1
apc.cross_project_handoff_check.v1
apc.checked_handoff_runtime_demo.v1
apc.release_artifacts.v1
apc.release_artifacts_summary.v1
apc.release_evidence_smoke.v1
```

## Release Use

For a tag candidate, keep:

```text
/tmp/apc-release-verify.json
/tmp/apc-release-verify-full.json
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-handoff-fixtures.json
/tmp/apc-release-artifacts.json
```

The release notes should reference this artifact contract when a public tag is
prepared.

## 0.2 Candidate Artifacts

For a `0.2` candidate, keep:

```text
/tmp/apc-release-verify-full.json
/tmp/apc-release-verify.json
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-handoff-fixtures.json
/tmp/apc-release-artifacts-0-2.json
/tmp/apc-release-artifacts-summary-0-2.json
/tmp/apc-release-evidence-smoke-0-2.json
/tmp/apc-benchmark-sweep.json
/tmp/apc-benchmark-sweep-summary.json
/tmp/apc-problem-family-fixtures.json
```

0.2 collection commands:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/collect_release_artifacts.py --tag v0.2.0-alpha.N --out /tmp/apc-release-artifacts-0-2.json
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts-0-2.json --out /tmp/apc-release-artifacts-summary-0-2.json
python3 scripts/smoke_release_evidence.py --tag v0.2.0-alpha.N --out /tmp/apc-release-evidence-smoke-0-2.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-benchmark-sweep.json
PYTHONPATH=src python3 scripts/inspect_benchmark_sweep.py /tmp/apc-benchmark-sweep.json --out /tmp/apc-benchmark-sweep-summary.json
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
```

0.2 artifact checks include:

```text
docs/RELEASE_CHECKLIST_0_2.md
docs/RELEASE_NOTES_0_2_DRAFT.md
docs/RELEASE_ARCHIVE_0_2.md
benchmark sweep evidence
problem-family fixture evidence
```

Maintenance tags should also keep:

```text
docs/MAINTENANCE_RELEASES.md
docs/RELEASE_CHECKLIST_0_2.md
docs/RELEASE_NOTES_0_2_DRAFT.md
docs/RELEASE_ARCHIVE_0_2.md
docs/TAG_EXECUTION_0_2.md
docs/POST_0_2_RUNTIME_PLAN.md
docs/RUNTIME_CONTRACT.md
src/apc/runtime_qubo_cpu.py
tests/test_qubo_cpu_reference_contract.py
tests/test_release_checklist_0_2.py
tests/test_release_artifacts_0_2.py
tests/test_tag_execution_0_2.py
tests/test_post_0_2_runtime_plan.py
tests/test_maintenance_releases.py
tests/test_runtime_contract.py
tests/test_operator_call_ledger.py
tests/test_runtime_status.py
tests/test_native_host_abi.py
tests/test_native_cpu_operator_shim.py
tests/test_native_binding_probe.py
docs/CUDA_OPERATOR_PARITY.md
tests/cuda/test_cuda_arch_config.py
tests/cuda/test_linear_csr_eval.py
tests/cuda/test_projection.py
tests/cuda/test_penalty_reduce.py
docs/BENCHMARK_SWEEPS.md
benchmarks/sweeps/binary_milp_smoke.json
scripts/run_benchmark_sweep.py
scripts/inspect_benchmark_sweep.py
tests/test_benchmark_sweep.py
tests/test_benchmark_sweep_runner.py
tests/test_benchmark_sweep_report.py
src/apc/readings/maxsat.py
examples/specs/maxsat_tiny.json
docs/PROBLEM_FAMILIES.md
tests/test_maxsat_runtime_route.py
src/apc/readings/qubo.py
examples/specs/qubo_tiny.json
tests/test_qubo_spec_lowering.py
scripts/list_problem_family_fixtures.py
examples/handoff/problem_family_fixtures.v1.json
tests/test_problem_family_fixture_set.py
```

## Reader

The reader emits a compact factual summary:

```text
schema: apc.release_artifacts_summary.v1
source_schema
source_path
status
tag
commit
artifact_count
artifact_schemas
fixture_count
check_count
failed_checks
notes
```

The reader reports the evidence that is present in the collected artifact. It
does not infer release quality or compatibility beyond the recorded checks.

## Smoke Command

The smoke command runs:

```text
scripts/verify_public_release.py
scripts/collect_release_artifacts.py
scripts/inspect_release_artifacts.py
```

It emits:

```text
schema: apc.release_evidence_smoke.v1
status
tag
mode
paths
steps
notes
```

The smoke report records output paths and step return codes. If any step fails,
later evidence steps are skipped and the report status is `failed`.

## Maintenance Tags

Maintenance release procedures are recorded in:

```text
docs/MAINTENANCE_RELEASES.md
```

The procedure uses the smoke command as the compact evidence route for 0.1.x
patch tags.
