# GPU-Native Constraint Tensor Fields

GPU-Native Constraint Tensor Fields is a public research scaffold for
constraint-repair runtimes that are designed around batch state evaluation,
explicit operator boundaries, CPU reference behavior, and optional CUDA parity.

The project is not a drop-in replacement for existing MIP, SAT, MaxSAT, QUBO,
or CP-SAT solvers. It is a compact native route for experimenting with:

```text
problem spec
-> CTIR lowering
-> layout planning
-> operator registry
-> repair runtime
-> validation ledger
-> benchmark evidence
```

## Current Version

```text
tag: v0.2.0-alpha.0
track: 0.2 Native Runtime Buildout
tag_commit: 795e051f92c87b19f7827410f223dea6a7450fcc
```

The 0.2 track includes:

```text
native problem specs
CTIR lowering
CPU reference runtime
CLI validation and run path
runtime execution contract
operator call ledger
runtime status codes
optional C++ host ABI skeleton
optional native CPU shim probe
CUDA operator parity smoke tests
benchmark sweep runner and reader
MaxSAT runtime route
QUBO spec and lowering route
problem-family fixture index
release evidence collector, reader, smoke command, and tag procedure
```

QUBO execution is still planned. CUDA parity is only added after a matching CPU
reference exists. Benchmark reports remain factual and do not make broad
accelerator comparison claims without complete timing evidence.

## Quickstart

From the repository root:

```bash
PYTHONPATH=src python3 -m apc.cli validate examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli inspect-ctir examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli run examples/specs/binary_milp_tiny.json --backend cpu
```

Run the standard benchmark:

```bash
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-bench.json --max-iters 2
```

Run the vector-native demo benchmark:

```bash
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo-bench.json
```

Run the benchmark sweep smoke path:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-benchmark-sweep.json
PYTHONPATH=src python3 scripts/inspect_benchmark_sweep.py /tmp/apc-benchmark-sweep.json --out /tmp/apc-benchmark-sweep-summary.json
```

More first-run commands are in [docs/QUICKSTART.md](docs/QUICKSTART.md).

## Problem Families

The current public fixture set covers:

```text
binary_milp
maxsat
qubo
```

Inspect the fixture index:

```bash
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
```

See [docs/PROBLEM_FAMILIES.md](docs/PROBLEM_FAMILIES.md) for route status and
limits.

## Runtime Shape

The runtime keeps a small set of public concepts:

```text
StatePool
BranchTensor
ReductionGate
InterfaceProjection
RuntimeContract
OperatorCallLedger
RuntimeStatus
```

The CPU reference path is the behavioral baseline. CUDA paths are checked
against CPU references on small cases and skip cleanly when CUDA tooling is not
available.

## Optional Native And CUDA Work

Native host scaffolding:

```text
native/include/apc_runtime.hpp
native/src/cpu_operator_shim.cpp
scripts/probe_native_host.py
```

CUDA parity scaffolding:

```text
cuda/src/linear_csr_eval.cu
cuda/src/projection.cu
cuda/src/violation_reduce.cu
tests/cuda/
```

CUDA tests are evidence checks, not performance claims.

## Release Evidence

Run the public verifier:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
```

Collect and inspect release artifacts:

```bash
python3 scripts/collect_release_artifacts.py --tag v0.2.0-alpha.0 --out /tmp/apc-release-artifacts-0-2.json
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts-0-2.json --out /tmp/apc-release-artifacts-summary-0-2.json
```

Run the compact evidence route:

```bash
python3 scripts/smoke_release_evidence.py --tag v0.2.0-alpha.0 --out /tmp/apc-release-evidence-smoke-0-2.json
```

The 0.2 archive is recorded in
[docs/RELEASE_ARCHIVE_0_2.md](docs/RELEASE_ARCHIVE_0_2.md).

## Next Stage

The next planned track is reference-first runtime expansion:

```text
QUBO CPU reference execution
-> additional CPU reference routes
-> broader CUDA parity
-> benchmark sweep expansion
-> problem-family fixture expansion
-> public 0.3 release evidence
```

See [docs/POST_0_2_RUNTIME_PLAN.md](docs/POST_0_2_RUNTIME_PLAN.md).

## License, Citation, And Origin

License: MIT. See [LICENSE](LICENSE).

Source lineage and citation files:

```text
CITATION.cff
NOTICE
docs/ORIGIN.md
```
