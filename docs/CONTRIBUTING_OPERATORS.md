# Contributing Operators And Families

This guide describes the public order for adding one problem family or one
operator. Keep extensions small, checked, and evidence-backed.

## Public Order

Use this order:

```text
spec
-> lowering
-> CPU reference
-> tests
-> fixtures
-> CLI route
-> benchmark or run artifact evidence
-> optional CUDA parity
-> release evidence
```

Do not add a CUDA parity target before the matching CPU reference exists.

## Add A Problem Family

1. Add a tiny JSON spec under `examples/specs/`.
2. Add a reader or lowering route under `src/apc/readings/`.
3. Lower into public CTIR structures from `src/apc/ctir.py`.
4. Add a deterministic CPU reference route.
5. Add focused tests for validation, lowering, unsupported fields, and runtime evidence.
6. Add fixture metadata in `examples/handoff/problem_family_fixtures.v1.json`.
7. Add the route to `apc run --family auto` only after the CPU route is checked.
8. Add benchmark sweep evidence when the route is stable enough to time.

Required public fields:

```text
schema
problem_family
backend
status
source_path
config
ledger
notes
```

Unsupported fields should fail with structured status or clear validation
errors.

## Add An Operator

1. Name the operator in the public runtime contract.
2. Add or identify a CPU reference function.
3. Add JSON-ready operator call ledger evidence.
4. Add tests for input shape, output shape, status, and deterministic behavior.
5. Add optional native host bridge fields only if the request/result shape is clear.
6. Add optional CUDA parity only after CPU behavior is checked.

Operator evidence should name:

```text
operator
problem_family
backend
inputs
outputs
status
timing_fields
reference_route
```

## Add CUDA Parity

CUDA parity must stay narrow:

```text
one operator
one CPU reference
one tiny fixture
one differential test
clean skip without nvcc or a CUDA device
```

Update:

```text
cuda/include/apc_runtime.h
cuda/src/
tests/cuda/
docs/CUDA_OPERATOR_PARITY.md
scripts/inspect_cuda_parity.py expectations when needed
```

CUDA docs and tests should record timing fields when measured, but should not
infer performance from correctness evidence.

## Add Release Evidence

When adding a public surface, update the smallest relevant set:

```text
docs/PROBLEM_FAMILIES.md
docs/RUNTIME_CONTRACT.md
docs/CUDA_OPERATOR_PARITY.md
docs/BENCHMARK_SWEEPS.md
docs/RELEASE_ARTIFACTS.md
scripts/collect_release_artifacts.py
tests/
```

For runtime behavior, prefer producing one of:

```text
runtime report
run artifact directory
benchmark sweep report
CUDA parity report
fixture index
```

## Boundaries

Do not add:

```text
drop-in replacement claims
solver compatibility promises before a checked adapter exists
performance claims without complete timing evidence
large CUDA kernels without CPU differential tests
private research-system terms
```

Keep examples tiny and inspectable. A good contribution should be easy to run
from the repository root and easy to summarize in release evidence.
