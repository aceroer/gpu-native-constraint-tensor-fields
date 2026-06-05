# 0.3 Release Notes Draft

## Scope

`0.3` is the 0.3 Reference-First Runtime Expansion release track. It turns QUBO
into a deterministic CPU reference route, expands MaxSAT ledger evidence,
selects and starts CUDA parity for narrow operators, and broadens benchmark and
fixture evidence.

## Highlights

```text
QUBO CPU reference execution route.
QUBO runtime ledger and release artifact evidence.
MaxSAT deterministic ledger-ready CPU route.
CUDA parity target selection for QUBO and MaxSAT.
QUBO CUDA energy parity smoke.
MaxSAT CUDA clause-evaluation parity smoke.
Benchmark sweep configs for binary_milp, qubo, and maxsat.
Problem-family fixtures with runtime and parity evidence paths.
0.3 release checklist and tag-readiness procedure.
```

## Stable Evidence Commands

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/collect_release_artifacts.py --tag v0.3.0-alpha.N --out /tmp/apc-release-artifacts-0-3.json
python3 scripts/smoke_release_evidence.py --tag v0.3.0-alpha.N --out /tmp/apc-release-evidence-smoke-0-3.json
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/qubo_smoke.json --out /tmp/apc-benchmark-sweep-qubo.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/maxsat_smoke.json --out /tmp/apc-benchmark-sweep-maxsat.json
```

## Candidate

```text
candidate_tag: v0.3.0-alpha.N
verified_commit: fill from /tmp/apc-release-artifacts-0-3.json commit
release_verifier_full_artifact: /tmp/apc-release-verify-full.json
release_artifact_report: /tmp/apc-release-artifacts-0-3.json
release_evidence_smoke_report: /tmp/apc-release-evidence-smoke-0-3.json
problem_family_fixture_index: examples/handoff/problem_family_fixtures.v1.json
qubo_sweep_summary: /tmp/apc-benchmark-sweep-qubo.json
maxsat_sweep_summary: /tmp/apc-benchmark-sweep-maxsat.json
```

## Current Limits

```text
No full MIP, MaxSAT, or QUBO optimality proof.
No drop-in replacement for existing solvers.
QUBO and MaxSAT reference routes are small deterministic evidence routes.
CUDA evidence is operator parity on narrow targets.
No broad accelerator comparison claim is made without complete timing evidence.
External adapter surfaces remain narrow public handoff sketches.
```

## Release Gate

The public `0.3` tag should only be created after:

```text
docs/RELEASE_CHECKLIST_0_3.md is satisfied.
Release verifier status is ok.
Release artifact collector status is ok.
Evidence smoke status is ok.
Problem-family fixture index status is ok.
Public terminology boundary scan is empty.
```

## Next Work After 0.3

```text
QUBO move-scoring CUDA parity.
MaxSAT CUDA parity reporting.
Expanded timing probes only after copy and kernel timing are complete.
Native host integration for broader runtime routes.
```
