# Next Major Stage

This document plans the next major stage after the release-evidence handoff
track. It assumes the project may need to be advanced by one maintainer for a
while, so every step should remain small, verifiable, and public-only.

## Current Planning Pointer

The active next-stage route after the 0.3 reference-first runtime expansion is:

```text
docs/POST_0_3_RUNTIME_PLAN.md
```

That plan names the 0.4 stage as Native Runtime Consolidation and starts with
QUBO CUDA move scoring parity.

The historical 0.2 buildout plan remains below as the completed route that
established the public runtime contract, native host probes, CUDA parity shape,
benchmark sweeps, and problem-family expansion.

## Stage Name

```text
0.2 Native Runtime Buildout
```

## Stage Goal

Turn the current research scaffold into a compact native runtime that can carry
real operator work without losing the verification discipline already present in
the repository.

The project should keep this order:

```text
release evidence reader
-> runtime execution contract
-> C++ host runtime skeleton
-> CUDA operator parity
-> benchmark sweeps
-> second problem-family runtime route
-> public 0.2 tag
```

## Position Before This Stage

Already in place:

```text
native problem specs
CTIR lowering
CPU reference runtime
CLI path
CUDA build skeleton
CPU/GPU differential-test shape
layout planning and materialization
operator registry
state pool
branch tensor
reduction gate
interface projection
benchmark reports
release verifier
release artifact collector
handoff fixture evidence
```

Still missing:

```text
release artifact reader
stable runtime execution contract
C++ host runtime boundary
CUDA operator parity beyond skeleton tests
repeatable benchmark sweep reports
larger problem-family examples
packaged 0.2 release evidence
```

## Workstream A: Release Evidence Closure

Purpose: finish the 0.1 evidence route so future tags are cheap to inspect.

Phases:

```text
Phase 37: Release Evidence Reader
Phase 38: Release Evidence Smoke Command
Phase 39: 0.1.x Maintenance Tag Procedure
```

Deliverable shape:

```text
scripts/inspect_release_artifacts.py
tests/test_release_artifact_reader.py
docs/RELEASE_ARTIFACTS.md
docs/MAINTENANCE_RELEASES.md
```

Acceptance:

```text
Reader consumes apc.release_artifacts.v1.
Reader reports status, tag, commit, schemas, and fixture count.
Smoke command can be run after the verifier and collector.
Maintenance release steps remain factual and evidence-based.
```

## Workstream B: Runtime Execution Contract

Purpose: define the exact public contract between CTIR, layout materialization,
operators, state pools, branch routes, and ledgers before adding heavier native
code.

Phases:

```text
Phase 40: Runtime Execution Contract
Phase 41: Operator Call Ledger
Phase 42: Runtime Error and Status Codes
```

Deliverable shape:

```text
src/apc/runtime_contract.py
src/apc/operator_call_ledger.py
docs/RUNTIME_CONTRACT.md
tests/test_runtime_contract.py
```

Acceptance:

```text
Every runtime step has named inputs, outputs, status, and timing fields.
Operator calls are ledgered without changing algorithm results.
Errors are structured and JSON-ready.
The CPU runtime continues to pass existing tests.
```

## Workstream C: C++ Host Runtime Skeleton

Purpose: prepare for efficient host-side execution without replacing the Python
reference path.

Phases:

```text
Phase 43: C++ Host ABI Header
Phase 44: C++ CPU Operator Shim
Phase 45: Python Binding Probe
```

Deliverable shape:

```text
native/include/apc_runtime.hpp
native/src/runtime_status.cpp
native/src/cpu_operator_shim.cpp
native/CMakeLists.txt
tests/native/
```

Acceptance:

```text
C++ build is optional and skips cleanly when unavailable.
Host ABI mirrors the public operator registry.
Python tests can call a tiny status or operator probe when built.
The Python CPU reference remains the source of behavioral truth.
```

## Workstream D: CUDA Operator Parity

Purpose: move from CUDA skeletons to checked operator parity on small instances.

Phases:

```text
Phase 46: Linear CSR CUDA Parity
Phase 47: Projection CUDA Parity
Phase 48: Penalty Reduction CUDA Parity
```

Deliverable shape:

```text
cuda/src/linear_csr_eval.cu
cuda/src/projection.cu
cuda/src/violation_reduce.cu
tests/cuda/
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance:

```text
Each CUDA operator has a CPU reference test.
Small random cases match within explicit tolerance.
CUDA tests skip cleanly without nvcc or a CUDA device.
Reports separate kernel time, copy time, and end-to-end time.
```

## Workstream E: Benchmark Sweeps

Purpose: make performance evidence repeatable before making any public
performance claim.

Phases:

```text
Phase 49: Benchmark Sweep Config
Phase 50: Benchmark Sweep Runner
Phase 51: Benchmark Sweep Report
```

Deliverable shape:

```text
benchmarks/sweeps/
scripts/run_benchmark_sweep.py
scripts/inspect_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep.py
tests/test_benchmark_sweep_runner.py
tests/test_benchmark_sweep_report.py
```

Acceptance:

```text
Sweep configs are JSON-ready and checked.
Sweep output records machine, backend, timing, and problem metadata.
CPU and CUDA results use the same schema.
Reports avoid acceleration claims without complete timing evidence.
```

## Workstream F: Problem-Family Expansion

Purpose: prove that the native path is not tied to one tiny example.

Phases:

```text
Phase 52: MaxSAT Runtime Route
Phase 53: QUBO Spec and Lowering
Phase 54: Problem-Family Fixture Set
```

Deliverable shape:

```text
src/apc/readings/maxsat.py
src/apc/readings/qubo.py
examples/specs/
docs/PROBLEM_FAMILIES.md
examples/handoff/
tests/test_problem_families.py
```

Acceptance:

```text
Each family lowers through native specs or CTIR.
Each family has a CPU reference route.
Each family has at least one benchmark or inspection report.
Unsupported features fail loudly.
```

## Workstream G: Public 0.2 Release

Purpose: close the stage with a release that is easy for outside contributors to
inspect and reproduce.

Phases:

```text
Phase 55: 0.2 Release Checklist
Phase 56: 0.2 Artifact Collection
Phase 57: 0.2 Public Tag
```

Deliverable shape:

```text
docs/RELEASE_CHECKLIST_0_2.md
docs/RELEASE_NOTES_0_2_DRAFT.md
docs/RELEASE_ARCHIVE_0_2.md
```

Acceptance:

```text
Release verifier passes.
Artifact collector passes.
Evidence reader summarizes the collected artifact.
Release notes state limits and non-goals clearly.
The tag points to the checked commit.
```

## Solo Maintainer Rules

Use these rules if one maintainer carries the full stage:

```text
One phase per commit.
One new public contract per phase.
Every new runtime surface gets a test.
Every CUDA path has a CPU reference.
Every benchmark separates copy, kernel, layout, and end-to-end time.
Every public doc passes the terminology boundary.
No compatibility promise is added before a checked adapter exists.
```

## Immediate Next Step

Phase 58 is now the planning bridge into the next major public runtime stage:

```text
docs/POST_0_2_RUNTIME_PLAN.md
docs/NEXT_MAJOR_STAGE.md
tests/test_post_0_2_runtime_plan.py
```

This plans the next public runtime expansion after the 0.2 closure track.

After Phase 58, continue with Phase 59:

```text
QUBO CPU reference contract
docs/POST_0_2_RUNTIME_PLAN.md
tests/test_qubo_cpu_reference_contract.py
```

The next stage is reference-first: QUBO CPU reference execution comes before
broader CUDA parity, and benchmark sweep expansion stays factual until complete
timing evidence exists.
