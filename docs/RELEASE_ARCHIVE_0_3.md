# 0.3 Release Archive Draft

This document is the durable handoff archive draft for a future public `0.3`
tag.

It is a draft until tag creation and remote tag verification succeed.

## Candidate Tag

```text
candidate_tag: v0.3.0-alpha.N
candidate_commit: fill from git rev-parse HEAD
tag_kind: pending
release_artifact_schema: apc.release_artifacts.v1
release_artifact_summary_schema: apc.release_artifacts_summary.v1
release_verifier_schema: apc.public_release_verification.v1
```

## Required Evidence Paths

```text
/tmp/apc-release-verify-full.json
/tmp/apc-release-verify.json
/tmp/apc-qubo-runtime.json
/tmp/apc-handoff-fixtures.json
/tmp/apc-release-artifacts-0-3.json
/tmp/apc-release-artifacts-summary-0-3.json
/tmp/apc-release-evidence-smoke-0-3.json
/tmp/apc-benchmark-sweep-binary-milp.json
/tmp/apc-benchmark-sweep-qubo.json
/tmp/apc-benchmark-sweep-maxsat.json
/tmp/apc-problem-family-fixtures.json
```

## Reproduce Candidate Evidence

From the repository root:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
PYTHONPATH=src python3 scripts/list_handoff_fixtures.py --out /tmp/apc-handoff-fixtures.json
python3 scripts/collect_release_artifacts.py --tag v0.3.0-alpha.N --out /tmp/apc-release-artifacts-0-3.json
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts-0-3.json --out /tmp/apc-release-artifacts-summary-0-3.json
python3 scripts/smoke_release_evidence.py --tag v0.3.0-alpha.N --out /tmp/apc-release-evidence-smoke-0-3.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-benchmark-sweep-binary-milp.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/qubo_smoke.json --out /tmp/apc-benchmark-sweep-qubo.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/maxsat_smoke.json --out /tmp/apc-benchmark-sweep-maxsat.json
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
```

## Required Schemas

```text
apc.public_release_verification.v1
apc.release_artifacts.v1
apc.release_artifacts_summary.v1
apc.release_evidence_smoke.v1
apc.qubo_cpu_reference_execution.v1
apc.maxsat_runtime_route.v1
apc.benchmark_sweep.v1
apc.benchmark_sweep_summary.v1
apc.problem_family_fixture_index.v1
```

## Candidate Checks

```text
release verifier status: ok
release artifact status: ok
release artifact summary status: ok
release evidence smoke status: ok
benchmark sweep statuses: ok
problem-family fixture index status: ok
public terminology boundary scan: empty
```

## Tag Verification

After a tag is created and pushed, record:

```text
git rev-parse v0.3.0-alpha.N^{commit}
git rev-parse HEAD
git ls-remote --tags origin 'v0.3.0-alpha.N*'
```

The local tag commit, remote peeled tag commit, and artifact report commit must
match before this draft becomes a final archive.

## Limits

```text
No full MIP, MaxSAT, or QUBO optimality proof.
No drop-in replacement for existing solvers.
CUDA evidence is narrow operator parity, not full runtime coverage.
No accelerator comparison claim is made without complete timing evidence.
```
