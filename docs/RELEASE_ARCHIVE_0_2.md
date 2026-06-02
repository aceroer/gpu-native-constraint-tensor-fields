# 0.2 Release Archive

This document is the durable handoff archive for the public `0.2` tag.

The tag has been created, pushed, and verified against the release artifact
commit.

## Tag

```text
tag: v0.2.0-alpha.0
tag_commit: 795e051f92c87b19f7827410f223dea6a7450fcc
tag_kind: annotated
release_artifact_schema: apc.release_artifacts.v1
release_artifact_summary_schema: apc.release_artifacts_summary.v1
release_verifier_schema: apc.public_release_verification.v1
```

## Required Evidence Paths

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

## Reproduce Candidate Evidence

From the repository root:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
PYTHONPATH=src python3 scripts/list_handoff_fixtures.py --out /tmp/apc-handoff-fixtures.json
python3 scripts/collect_release_artifacts.py --tag v0.2.0-alpha.0 --out /tmp/apc-release-artifacts-0-2.json
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts-0-2.json --out /tmp/apc-release-artifacts-summary-0-2.json
python3 scripts/smoke_release_evidence.py --tag v0.2.0-alpha.0 --out /tmp/apc-release-evidence-smoke-0-2.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-benchmark-sweep.json
PYTHONPATH=src python3 scripts/inspect_benchmark_sweep.py /tmp/apc-benchmark-sweep.json --out /tmp/apc-benchmark-sweep-summary.json
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
```

## Required Schemas

```text
apc.public_release_verification.v1
apc.release_artifacts.v1
apc.release_artifacts_summary.v1
apc.release_evidence_smoke.v1
apc.benchmark.v1
apc.vector_demo_benchmark.v1
apc.handoff_fixture_index.v1
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
benchmark sweep status: ok
problem-family fixture index status: ok
public terminology boundary scan: empty
```

## Tag Verification

Verified commands:

```text
git rev-parse v0.2.0-alpha.0^{commit}
git rev-parse 795e051f92c87b19f7827410f223dea6a7450fcc
git ls-remote --tags origin 'v0.2.0-alpha.0*'
```

The local tag commit, remote peeled tag commit, and artifact report commit all
match:

```text
795e051f92c87b19f7827410f223dea6a7450fcc
```

## Included 0.2 Gates

```text
runtime execution contract
native host boundary
CUDA operator parity
benchmark sweeps
problem-family fixtures
0.2 checklist and notes
```

## Limits

```text
No full MIP, MaxSAT, or QUBO optimality proof.
No drop-in replacement for existing solvers.
QUBO execution remains planned.
No accelerator comparison claim is made without complete timing evidence.
```
