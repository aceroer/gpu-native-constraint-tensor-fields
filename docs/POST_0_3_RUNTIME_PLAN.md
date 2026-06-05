# Post-0.3 Runtime Plan

This document defines the public 0.4 route after the 0.3 reference-first
runtime expansion. It keeps the same rule as the earlier stages: every native
or CUDA step starts from a checked CPU reference, every public claim is backed by
evidence, and unsupported paths fail with structured status.

## Stage Name

```text
0.4 Native Runtime Consolidation
```

## Stage Goal

Move from small reference/parity routes into a compact native runtime lane that
outside contributors can extend without guessing the project order.

The stage order is:

```text
QUBO CUDA move scoring parity
-> CUDA parity report integration
-> runtime CLI family routing
-> run artifact writer
-> native host bridge consolidation
-> benchmark timing expansion
-> contributor extension guide
-> runtime debug tools
-> public 0.4 release evidence
```

## Position Before This Stage

Already in place:

```text
Binary MILP CPU repair runtime
QUBO CPU reference execution
MaxSAT CPU runtime route
QUBO CUDA energy parity smoke
MaxSAT CUDA clause-evaluation parity smoke
benchmark sweep runner and reports
problem-family fixture evidence
0.3 release checklist and tag-readiness documents
```

Still missing:

```text
none
```

## Workstream A: QUBO CUDA Move Scoring Parity

Purpose: make the next CUDA target exercise a useful local-search primitive,
not only whole-energy evaluation.

Deliverable shape:

```text
cuda/src/qubo_move_score.cu
tests/cuda/test_qubo_move_score.py
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance:

```text
QUBO CUDA move scoring parity matches the CPU reference on tiny fixtures.
Each tested move has an explicit bit index, old score, and candidate score.
CUDA tests skip cleanly without nvcc or a CUDA device.
No acceleration claim is made.
```

## Workstream B: CUDA Parity Report Integration

Purpose: keep CUDA evidence inspectable as the number of parity targets grows.

Deliverable shape:

```text
scripts/inspect_cuda_parity.py
docs/CUDA_OPERATOR_PARITY.md
tests/cuda/test_parity_report.py
```

Acceptance:

```text
Parity reports name operator, family, backend, reference route, and status.
Unavailable CUDA is recorded as unavailable, not hidden as success.
Timing fields separate kernel, copy, layout, and end-to-end durations when run.
The report remains useful on machines without CUDA.
```

## Workstream C: Runtime CLI Family Routing

Purpose: expose the implemented family routes through one stable public command
surface.

Deliverable shape:

```text
src/apc/cli.py
docs/QUICKSTART.md
tests/test_cli.py
```

Acceptance:

```text
CLI routing can run binary_milp, qubo, and maxsat examples.
Each route emits schema, family, backend, status, and evidence fields.
Unsupported family names fail with structured status.
The command remains small enough for quick local smoke runs.
```

## Workstream D: Run Artifact Writer

Purpose: make runtime outputs reproducible and easy to attach to release or
handoff evidence.

Deliverable shape:

```text
src/apc/run_artifacts.py
docs/RUNTIME_CONTRACT.md
tests/test_run_artifacts.py
```

Acceptance:

```text
Run outputs have a stable directory layout.
Each run writes inputs, result, ledger, timings, and metadata.
Artifact files are JSON-ready and deterministic for tiny fixtures.
Temporary or local machine paths do not leak into public examples.
```

## Workstream E: Native Host Bridge Consolidation

Purpose: turn the native host probes into a clearer extension point while
keeping Python references as behavioral truth.

Deliverable shape:

```text
native/include/apc_runtime.hpp
native/src/runtime_status.cpp
native/src/cpu_operator_shim.cpp
tests/native/
docs/RUNTIME_CONTRACT.md
```

Acceptance:

```text
Native host bridge names status, operator request, operator result, and timings.
Optional native builds skip cleanly when the toolchain is unavailable.
Python CPU references remain the source of expected values.
The bridge does not promise a stable external ABI before a checked adapter exists.
```

## Workstream F: Benchmark Timing Expansion

Purpose: collect factual timing evidence across the implemented public routes
before any performance language is added.

Deliverable shape:

```text
benchmarks/sweeps/
scripts/run_benchmark_sweep.py
scripts/inspect_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep_report.py
```

Acceptance:

```text
Benchmark reports cover binary_milp, qubo, and maxsat smoke fixtures.
Reports include backend, family, operator, status, and timing fields.
CUDA unavailable status remains explicit on non-CUDA machines.
Docs avoid performance claims without complete timing evidence.
```

## Workstream G: Contributor Extension Guide

Purpose: let interested readers add one problem family or operator without
reverse-engineering the repository.

Deliverable shape:

```text
docs/CONTRIBUTING_OPERATORS.md
docs/PROBLEM_FAMILIES.md
examples/specs/
tests/test_contributing_operators.py
```

Acceptance:

```text
The guide shows the public order: spec, lowering, CPU reference, tests, optional CUDA.
It names required docs, fixture metadata, and release evidence touch points.
It avoids solver compatibility and performance promises.
It keeps examples small and inspectable.
```

## Workstream H: Runtime Debug Tools

Purpose: make real-environment failures inspectable before the project grows
past tiny smoke examples.

Deliverable shape:

```text
src/apc/debug.py
scripts/inspect_runtime_debug.py
docs/DEBUGGING.md
tests/test_runtime_debug.py
```

Acceptance:

```text
Debug reports can inspect specs, lowered CTIR, layout summaries, ledgers, run artifacts, and status codes.
CUDA debug output records device availability, nvcc availability, selected arch, and skip reason.
Debug reports avoid local secrets and machine-specific paths in public examples.
Failure records include enough context to reproduce tiny fixture failures.
Every later version keeps an explicit debug-tooling checkpoint before release evidence.
```

## Workstream I: Public 0.4 Release Evidence

Purpose: close the stage with a tag candidate that can be reproduced by outside
readers.

Deliverable shape:

```text
docs/RELEASE_CHECKLIST_0_4.md
docs/RELEASE_NOTES_0_4_DRAFT.md
docs/RELEASE_ARCHIVE_0_4.md
docs/TAG_EXECUTION_0_4.md
```

Acceptance:

```text
Full release verifier passes.
CUDA parity checks pass or skip with explicit status.
Benchmark sweeps produce inspectable timing evidence.
Debug tooling can summarize runtime, CUDA, and artifact failures.
Release notes state limits and non-goals clearly.
The terminology boundary scan stays empty.
```

## Solo Maintainer Sequence

Use this sequence if one maintainer carries the stage:

```text
Phase 69: 0.4 route plan
Phase 70: QUBO CUDA move scoring parity
Phase 71: CUDA parity report integration
Phase 72: runtime CLI family routing
Phase 73: run artifact writer
Phase 74: native host bridge consolidation
Phase 75: benchmark timing expansion
Phase 76: contributor extension guide
Phase 77: runtime debug tools
Phase 78: 0.4 release checklist
Phase 79: 0.4 release evidence archive
```

## Ground Rules

```text
No CUDA parity route before the matching CPU reference exists.
Each CUDA target has a CPU reference test.
CUDA tests skip cleanly without nvcc or a CUDA device.
No acceleration claim is made without complete timing evidence.
No drop-in replacement claim is made.
No solver-compatibility promise is made before a checked adapter exists.
Public docs avoid private research-system terms.
Every version after 0.4 keeps a debug-tooling checkpoint in its release route.
```

## Immediate Next Step

Phase 70 should implement QUBO CUDA move scoring parity against the existing
QUBO CPU reference route. Keep the target tiny, exact where integer arithmetic
allows, and factual about CUDA availability.
