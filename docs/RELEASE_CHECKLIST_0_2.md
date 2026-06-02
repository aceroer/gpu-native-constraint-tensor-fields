# 0.2 Release Checklist

Use this checklist before creating a public `0.2` tag.

## Candidate

```text
candidate_tag: v0.2.0-alpha.N
candidate_commit: fill from git rev-parse HEAD
release_track: 0.2 Native Runtime Buildout
```

## Required Commands

Run the full verifier:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
```

Run the release artifact collector:

```bash
python3 scripts/collect_release_artifacts.py --tag v0.2.0-alpha.N --out /tmp/apc-release-artifacts-0-2.json
```

Run the evidence smoke command:

```bash
python3 scripts/smoke_release_evidence.py --tag v0.2.0-alpha.N --out /tmp/apc-release-evidence-smoke-0-2.json
```

## Gates

Runtime contract gate:

```text
docs/RUNTIME_CONTRACT.md
tests/test_runtime_contract.py
tests/test_operator_call_ledger.py
tests/test_runtime_status.py
```

Native host gate:

```text
native/include/apc_runtime.hpp
native/src/cpu_operator_shim.cpp
scripts/probe_native_host.py
tests/test_native_host_abi.py
tests/test_native_cpu_operator_shim.py
tests/test_native_binding_probe.py
```

CUDA parity gate:

```text
docs/CUDA_OPERATOR_PARITY.md
tests/cuda/test_linear_csr_eval.py
tests/cuda/test_projection.py
tests/cuda/test_penalty_reduce.py
```

Benchmark sweep gate:

```text
benchmarks/sweeps/binary_milp_smoke.json
scripts/run_benchmark_sweep.py
scripts/inspect_benchmark_sweep.py
tests/test_benchmark_sweep.py
tests/test_benchmark_sweep_runner.py
tests/test_benchmark_sweep_report.py
```

Problem-family fixture gate:

```text
docs/PROBLEM_FAMILIES.md
examples/handoff/problem_family_fixtures.v1.json
scripts/list_problem_family_fixtures.py
tests/test_problem_family_fixture_set.py
```

## Evidence Schemas

Required evidence schemas:

```text
apc.public_release_verification.v1
apc.release_artifacts.v1
apc.release_artifacts_summary.v1
apc.release_evidence_smoke.v1
apc.benchmark_sweep.v1
apc.benchmark_sweep_summary.v1
apc.problem_family_fixture_index.v1
```

## Stop Conditions

Do not create a public `0.2` tag if any item is true:

```text
Full verification fails.
Release artifact collection fails.
Evidence smoke fails.
Problem-family fixture index is missing binary_milp, maxsat, or qubo.
QUBO execution is presented as implemented instead of planned.
CUDA parity tests fail instead of skipping cleanly when CUDA tooling is unavailable.
Public docs add solver replacement promises.
Public docs add accelerator comparison claims without complete timing evidence.
```

## Result

Only create the tag after every gate has current evidence and the public
terminology boundary scan is empty.
