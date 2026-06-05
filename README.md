# GPU-Native Constraint Tensor Fields

GPU-Native Constraint Tensor Fields is a public research scaffold for
constraint-repair runtimes designed around batch state evaluation, explicit
operator boundaries, CPU reference behavior, and optional CUDA parity.

The project is not a drop-in replacement for existing MIP, SAT, MaxSAT, QUBO,
or CP-SAT solvers. It is a compact native route for experimenting with:

```text
problem spec
-> CTIR lowering
-> layout planning
-> operator registry
-> repair runtime
-> validation ledger
-> benchmark and debug evidence
```

## Current Version

```text
tag: v0.4.0-alpha.0
track: 0.4 Beta Real-Environment Split
tag_commit: b06ee935ce5deae64a40af651574bf8b5877cd26
```

The 0.4 track includes:

```text
binary_milp, maxsat, and qubo runtime routes
QUBO CPU reference execution
QUBO CUDA move-scoring parity target
CUDA parity report inspector
family-routed runtime CLI
stable run artifact directories
runtime debug reports
0.4 beta debug checkpoint
native host bridge request/result records
benchmark sweep runner and reader
contributor operator extension guide
release evidence collector, reader, smoke command, and tag procedure
```

CUDA tests are paired with CPU references on small cases and skip cleanly when
CUDA tooling or a CUDA device is unavailable. Benchmark and debug reports are
factual evidence surfaces; they do not make broad accelerator performance
claims.

## Quickstart

From the repository root:

```bash
PYTHONPATH=src python3 -m apc.cli validate examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli inspect-ctir examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli run examples/specs/binary_milp_tiny.json --backend cpu --max-iters 2
```

Run implemented public families through the routed CLI:

```bash
PYTHONPATH=src python3 -m apc.cli run examples/specs/qubo_tiny.json --family auto --max-iters 2 --ledger-out /tmp/apc-qubo-report.json
PYTHONPATH=src python3 -m apc.cli run examples/specs/maxsat_tiny.json --family auto --max-iters 2 --ledger-out /tmp/apc-maxsat-report.json
```

Write a stable artifact directory for a run:

```bash
PYTHONPATH=src python3 -m apc.cli run examples/specs/qubo_tiny.json --family auto --max-iters 2 --artifact-dir /tmp/apc-runs --run-id qubo_tiny
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
RunArtifacts
RuntimeDebugReport
```

The CPU reference path is the behavioral baseline. CUDA paths are checked
against CPU references on small cases, and environment gaps are recorded as
structured status instead of hidden success.

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
cuda/src/qubo_energy.cu
cuda/src/qubo_move_score.cu
scripts/inspect_cuda_parity.py
tests/cuda/
```

Inspect CUDA parity status:

```bash
PYTHONPATH=src python3 scripts/inspect_cuda_parity.py --out /tmp/apc-cuda-parity-report.json
```

CUDA tests are evidence checks, not performance claims.

## Debug Evidence

Generate a runtime debug report:

```bash
PYTHONPATH=src python3 scripts/inspect_runtime_debug.py examples/specs/qubo_tiny.json --out /tmp/apc-runtime-debug.json
```

The 0.4 beta checkpoint records:

```text
compute mode
host role
host compiler readiness
CUDA differential-test status
release artifact status
PCI/HAL boundary status
```

The current beta route treats Windows as an orchestration layer unless a checked
adapter proves otherwise. TCC or headless CUDA remains a preferred compute lane
where supported hardware is available; WDDM and missing TCC are recorded as
environment facts, not operator failures.

See [docs/DEBUGGING.md](docs/DEBUGGING.md) and
[docs/POST_0_4_BETA_PLAN.md](docs/POST_0_4_BETA_PLAN.md).

## Release Evidence

Run the public verifier:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full-0-4.json
```

Collect and inspect release artifacts:

```bash
python3 scripts/collect_release_artifacts.py --tag v0.4.0-alpha.0 --verify /tmp/apc-release-verify-full-0-4.json --out /tmp/apc-release-artifacts-0-4.json
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts-0-4.json --out /tmp/apc-release-artifacts-summary-0-4.json
```

The 0.4 archive is recorded in
[docs/RELEASE_ARCHIVE_0_4.md](docs/RELEASE_ARCHIVE_0_4.md).

## Next Stage

The next planned track is real-environment consolidation:

```text
TCC or headless CUDA evidence where supported hardware is available
-> WSL2 Linux-userspace smoke checks
-> Windows orchestration artifact handoff
-> broader CUDA parity targets
-> stronger runtime debug tools
-> public 0.5 release evidence
```

The public line stays at reproducible CUDA/HAL evidence. Lower-level hardware
control is not required for the open-source runtime to remain useful.

## License, Citation, And Origin

License: MIT. See [LICENSE](LICENSE).

Source lineage and citation files:

```text
CITATION.cff
NOTICE
docs/ORIGIN.md
```
