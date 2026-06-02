# 0.2 Release Notes Draft

## Scope

`0.2` is the 0.2 Native Runtime Buildout release track. It collects the public
runtime contract, native host boundary, CUDA parity checks, benchmark sweep
evidence, and problem-family fixtures into one reproducible release surface.

## Highlights

```text
Runtime execution contract with operator call ledger and runtime status codes.
C++ host ABI header and CPU operator shim probe.
Python native host probe.
CUDA parity records for linear CSR, projection, and penalty reduction targets.
Benchmark sweep config, runner, and reader.
MaxSAT public runtime route.
QUBO public spec and CTIR lowering route.
Problem-family fixture index for binary_milp, maxsat, and qubo.
Release artifact collector, reader, and smoke command.
```

## Stable Evidence Commands

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/collect_release_artifacts.py --tag v0.2.0-alpha.N --out /tmp/apc-release-artifacts-0-2.json
python3 scripts/smoke_release_evidence.py --tag v0.2.0-alpha.N --out /tmp/apc-release-evidence-smoke-0-2.json
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-benchmark-sweep.json
PYTHONPATH=src python3 scripts/inspect_benchmark_sweep.py /tmp/apc-benchmark-sweep.json --out /tmp/apc-benchmark-sweep-summary.json
```

## Candidate

```text
candidate_tag: v0.2.0-alpha.N
verified_commit: fill from /tmp/apc-release-artifacts-0-2.json commit
release_verifier_full_artifact: /tmp/apc-release-verify-full.json
release_artifact_report: /tmp/apc-release-artifacts-0-2.json
release_evidence_smoke_report: /tmp/apc-release-evidence-smoke-0-2.json
problem_family_fixture_index: examples/handoff/problem_family_fixtures.v1.json
benchmark_sweep_summary: /tmp/apc-benchmark-sweep-summary.json
```

## Current Limits

```text
No full MIP, MaxSAT, or QUBO optimality proof.
No drop-in replacement for existing solvers.
QUBO execution is planned; QUBO currently has checked spec and lowering evidence.
CUDA evidence is parity and timing-accounting evidence on narrow targets.
No broad accelerator comparison claim is made without complete timing evidence.
External adapter surfaces remain narrow public handoff sketches.
```

## Release Gate

The public `0.2` tag should only be created after:

```text
docs/RELEASE_CHECKLIST_0_2.md is satisfied.
Release verifier status is ok.
Release artifact collector status is ok.
Evidence smoke status is ok.
Problem-family fixture index status is ok.
Public terminology boundary scan is empty.
```

## Next Work After 0.2

```text
0.2 artifact collection and archive.
0.2 public tag execution.
Additional problem-family fixtures.
Broader CUDA operator parity after CPU references are in place.
QUBO execution only after a tested CPU reference route exists.
```
