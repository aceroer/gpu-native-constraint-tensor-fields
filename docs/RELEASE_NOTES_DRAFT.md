# Release Notes Draft

## Scope

This draft summarizes the current public state of the GPU-native constraint
runtime prototype.

## Highlights

```text
Native binary MILP problem specs.
CTIR lowering and inspection.
CPU reference repair runtime.
Device layout planning and layout materialization.
Operator registry with CPU references and CUDA ABI names.
CUDA skeleton and unavailable-path benchmark handling.
Benchmark harness with explicit timing fields.
MaxSAT reading path and CPU repair example.
StatePool, BranchTensor, ReductionGate, and InterfaceProjection layers.
Vector-native repair demo and projected demo benchmark report.
Public quickstart and handoff docs.
Release verifier and release checklist for tag readiness.
Release artifact contract for repeatable tag evidence.
GPU-side vAgentRT handoff consumer with JSON-only dependency boundary.
Checked handoff runtime demo for StatePool and selected action inspection.
Checked handoff fixture archive for repeatable demo evidence.
Problem-family binary_milp handoff fixture with JSON-only inspection boundary.
```

## Stable Commands

```bash
PYTHONPATH=src python3 -m apc.cli validate examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli run examples/specs/binary_milp_tiny.json --max-iters 2 --ledger-out /tmp/apc-ledger.json
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-bench.json --max-iters 2
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo-bench.json
PYTHONPATH=src python3 scripts/check_vagent_handoff.py examples/handoff/vagent_apc_handoff_report.v1.json --out /tmp/apc-vagent-handoff-check.json
PYTHONPATH=src python3 scripts/run_checked_handoff_demo.py /tmp/apc-vagent-handoff-check.json --out /tmp/apc-checked-handoff-demo.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.N --out /tmp/apc-release-artifacts.json
```

## Release Readiness

```text
The release verifier emits schema apc.public_release_verification.v1.
The release checklist names tag, docs, tests, and benchmark artifacts.
The release artifact contract emits schema apc.release_artifacts.v1.
Full verification is available through scripts/verify_public_release.py --full.
```

## Tag Candidate

```text
candidate_tag: v0.1.0-alpha.0
verified_commit: fill from /tmp/apc-release-artifacts.json commit
release_verifier_artifact: /tmp/apc-release-verify.json
release_verifier_full_artifact: /tmp/apc-release-verify-full.json
release_artifact_report: /tmp/apc-release-artifacts.json
cpu_benchmark_artifact: /tmp/apc-release-bench.json
vector_demo_benchmark_artifact: /tmp/apc-release-vector-demo-bench.json
```

## Final Tag

```text
final_tag: v0.1.0-alpha.0
tag_target: fill from /tmp/apc-release-artifacts.json commit
release_verifier_artifact: /tmp/apc-release-verify.json
release_verifier_full_artifact: /tmp/apc-release-verify-full.json
release_artifact_report: /tmp/apc-release-artifacts.json
cpu_benchmark_artifact: /tmp/apc-release-bench.json
vector_demo_benchmark_artifact: /tmp/apc-release-vector-demo-bench.json
```

## Release Archive

```text
archived_tag: v0.1.0-alpha.0
archived_tag_commit: b051c20b38ff19cf99992daa72dc1e9558ec7b84
archive_doc: docs/RELEASE_ARCHIVE.md
release_artifact_report: /tmp/apc-release-artifacts.json
release_verifier_full_artifact: /tmp/apc-release-verify-full.json
```

## Cross-Project Handoff

```text
gpu_tag: v0.1.0-alpha.0
gpu_release_artifact_schema: apc.release_artifacts.v1
paired_project: vAgentRT
paired_tag: v0.1.1
paired_cuda_smoke: Colab T4 deterministic smoke status ok
paired_windows_sm89_cuda_smoke: RTX 4070 Laptop GPU deterministic smoke status ok
gpu_windows_sm89_cuda_benchmark: RTX 4070 Laptop GPU benchmark backend available
handoff_doc: docs/CROSS_PROJECT_HANDOFF.md
handoff_consumer: scripts/check_vagent_handoff.py
handoff_check_schema: apc.cross_project_handoff_check.v1
checked_handoff_demo: scripts/run_checked_handoff_demo.py
checked_handoff_demo_schema: apc.checked_handoff_runtime_demo.v1
checked_handoff_fixture_input: examples/handoff/vagent_apc_handoff_report.v1.json
checked_handoff_fixture_check: examples/handoff/apc_handoff_check.v1.json
checked_handoff_fixture_demo: examples/handoff/apc_checked_handoff_demo.v1.json
problem_family_handoff_fixture_input: examples/handoff/vagent_binary_milp_handoff_report.v1.json
problem_family_handoff_fixture_check: examples/handoff/apc_binary_milp_handoff_check.v1.json
problem_family_handoff_fixture_demo: examples/handoff/apc_binary_milp_checked_handoff_demo.v1.json
status: cross-project handoff sketch without claiming drop-in compatibility
```

## Current Limits

```text
No full MIP optimality proof.
No drop-in replacement for existing solvers.
CUDA kernels are still narrow and guarded by CPU differential tests.
Compatibility adapters are intentionally narrow.
```

## Next Work

```text
Public benchmark sweeps.
Additional problem-family demos.
More CUDA operator coverage.
Broader CUDA coverage after CPU/CUDA differential tests are expanded.
Release artifact archiving for future public releases.
Release archive handoff for the first public tag.
Cross-project handoff sketch toward the paired vector-native runtime route.
Problem-family handoff fixture index for available public fixtures.
```
