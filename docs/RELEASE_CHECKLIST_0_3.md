# 0.3 Release Checklist

Use this checklist before creating a public `0.3` tag.

## Candidate

```text
candidate_tag: v0.3.0-alpha.N
candidate_commit: fill from git rev-parse HEAD
release_track: 0.3 Reference-First Runtime Expansion
```

## Required Commands

Run the full verifier:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
```

Run release artifact collection:

```bash
python3 scripts/collect_release_artifacts.py --tag v0.3.0-alpha.N --out /tmp/apc-release-artifacts-0-3.json
```

Run evidence smoke:

```bash
python3 scripts/smoke_release_evidence.py --tag v0.3.0-alpha.N --out /tmp/apc-release-evidence-smoke-0-3.json
```

Run 0.3 benchmark sweeps:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-benchmark-sweep-binary-milp.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/qubo_smoke.json --out /tmp/apc-benchmark-sweep-qubo.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/maxsat_smoke.json --out /tmp/apc-benchmark-sweep-maxsat.json
```

Run fixture evidence:

```bash
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
```

Run CUDA smoke checks:

```bash
APC_CUDA_ARCH=sm_89 PYTHONPATH=src python3 -m unittest tests.cuda.test_qubo_energy tests.cuda.test_clause_eval -v
```

## Gates

QUBO CPU reference gate:

```text
src/apc/runtime_qubo_cpu.py
tests/test_qubo_cpu_reference.py
tests/test_qubo_cpu_reference_contract.py
```

MaxSAT CPU reference gate:

```text
src/apc/readings/maxsat.py
tests/test_maxsat_runtime_route.py
```

CUDA parity gate:

```text
docs/CUDA_OPERATOR_PARITY.md
tests/cuda/test_parity_target_selection.py
tests/cuda/test_qubo_energy.py
tests/cuda/test_clause_eval.py
```

Benchmark sweep gate:

```text
benchmarks/sweeps/binary_milp_smoke.json
benchmarks/sweeps/qubo_smoke.json
benchmarks/sweeps/maxsat_smoke.json
scripts/run_benchmark_sweep.py
scripts/inspect_benchmark_sweep.py
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
apc.qubo_cpu_reference_execution.v1
apc.maxsat_runtime_route.v1
apc.benchmark_sweep.v1
apc.benchmark_sweep_summary.v1
apc.problem_family_fixture_index.v1
```

## Stop Conditions

Do not create a public `0.3` tag if any item is true:

```text
Full verification fails.
Release artifact collection fails.
Evidence smoke fails.
QUBO CPU reference execution is missing.
MaxSAT runtime ledger evidence is missing.
CUDA smoke tests fail instead of skipping cleanly when CUDA tooling is unavailable.
Benchmark sweep reports omit timing fields.
Public docs add solver replacement promises.
Public docs add accelerator comparison claims without complete timing evidence.
Public terminology boundary scan is not empty.
```

## Result

Only create the tag after every gate has current evidence and the public
terminology boundary scan is empty.
