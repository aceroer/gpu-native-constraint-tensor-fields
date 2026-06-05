# Post-0.2 Runtime Expansion Plan

This plan defines the public route after the 0.2 release-evidence track. It is
written for a period where one maintainer may need to carry most of the work.

## Stage Name

```text
0.3 Reference-First Runtime Expansion
```

## Stage Goal

Move from a checked scaffold into broader runtime coverage while keeping CPU
references as the behavioral source of truth.

The order is:

```text
QUBO CPU reference execution
-> additional CPU reference routes
-> broader CUDA parity
-> benchmark sweep expansion
-> problem-family fixture expansion
-> public 0.3 release evidence
```

## Ground Rules

```text
No drop-in replacement claim.
No solver-compatibility promise before a checked adapter exists.
No acceleration claim without complete timing evidence.
No CUDA parity route before the matching CPU reference exists.
No benchmark interpretation without kernel, copy, layout, and end-to-end fields.
```

## Workstream A: QUBO CPU Reference Execution

Purpose: turn QUBO lowering into a runnable CPU reference route.

Deliverables:

```text
src/apc/runtime_qubo_cpu.py
examples/specs/qubo_tiny.json
tests/test_qubo_cpu_reference.py
docs/PROBLEM_FAMILIES.md
```

Acceptance:

```text
QUBO CPU reference execution runs from a native spec.
The route records objective, penalty, move count, and final state.
Unsupported QUBO features fail with structured status codes.
The route does not promise solver compatibility.
```

## Workstream B: Additional CPU Reference Routes

Purpose: widen runtime coverage before widening CUDA coverage.

Targets:

```text
MaxSAT repair loop
binary MILP repair variants
small mixed problem-family inspection routes
```

Acceptance:

```text
Every route has deterministic fixture tests.
Every route emits ledger-ready status.
Every route keeps native problem specs inspectable.
Every route has a clear unsupported-feature path.
```

## Workstream C: Broader CUDA Parity

Purpose: add CUDA only where the CPU reference already exists.

Initial CUDA targets:

```text
QUBO energy evaluation
QUBO move scoring
MaxSAT clause violation evaluation
shared reduction helpers
```

Acceptance:

```text
Each CUDA target has a CPU reference test.
CUDA tests skip cleanly without nvcc or a CUDA device.
Small cases match within explicit tolerance.
Reports avoid performance claims without complete timing evidence.
```

## Workstream D: Benchmark Sweep Expansion

Purpose: make evidence repeatable across problem families.

Deliverables:

```text
benchmarks/sweeps/qubo_smoke.json
benchmarks/sweeps/maxsat_smoke.json
scripts/run_benchmark_sweep.py
scripts/inspect_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
```

Acceptance:

```text
Benchmark sweep reports include backend, problem family, machine, and timing.
Timing fields separate kernel, copy, layout, and end-to-end measurements.
Reports are factual and avoid acceleration claims.
Failed or skipped CUDA runs remain explicit in the output.
```

## Workstream E: Problem-Family Fixture Expansion

Purpose: give outside contributors small checked examples for each route.

Deliverables:

```text
examples/handoff/problem_family_fixtures.v1.json
scripts/list_problem_family_fixtures.py
docs/PROBLEM_FAMILIES.md
tests/test_problem_family_fixture_set.py
```

Acceptance:

```text
Each fixture names schema, route, status, and evidence path.
Each fixture is small enough for quick local checks.
Problem-family fixture records remain public-only.
Fixture docs avoid solver compatibility and performance claims.
```

## Workstream F: Public 0.3 Evidence

Purpose: close the next stage with the same evidence discipline as 0.1 and 0.2.

Deliverables:

```text
docs/RELEASE_CHECKLIST_0_3.md
docs/RELEASE_NOTES_0_3_DRAFT.md
docs/RELEASE_ARCHIVE_0_3.md
docs/TAG_EXECUTION_0_3.md
```

Acceptance:

```text
Full verifier passes.
Artifact collector includes the new runtime-plan evidence.
Benchmark sweep evidence is present but makes no acceleration claim.
Release notes state non-goals and unsupported routes clearly.
The public tag points to the checked commit.
```

## Solo Maintainer Sequence

Use this sequence if the project is carried by one maintainer:

```text
Phase 59: QUBO CPU reference contract
Phase 60: QUBO CPU execution route
Phase 61: QUBO runtime ledger evidence
Phase 62: MaxSAT CPU reference expansion
Phase 63: CUDA parity target selection
Phase 64: QUBO CUDA parity smoke
Phase 65: MaxSAT CUDA parity smoke
Phase 66: Benchmark sweep expansion
Phase 67: Fixture expansion
Phase 68: 0.3 release checklist
```

The sequence can be paused after any phase because each phase should produce one
small public artifact and one matching test.

Phase 59 output:

```text
src/apc/runtime_qubo_cpu.py
tests/test_qubo_cpu_reference_contract.py
```

This establishes the QUBO CPU reference contract. The executable route remains
Phase 60.

## Stop Conditions

Stop and repair before advancing if:

```text
The CPU reference route is missing for a planned CUDA target.
The verifier or boundary scan fails.
A benchmark report cannot separate timing fields.
A document implies broad solver compatibility.
A release note implies performance without complete timing evidence.
```
