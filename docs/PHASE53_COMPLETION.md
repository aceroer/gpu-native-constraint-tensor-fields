# Phase 53 Completion

Phase 53 added the QUBO spec and lowering route.

## Delivered

```text
src/apc/readings/qubo.py
examples/specs/qubo_tiny.json
docs/PROBLEM_FAMILIES.md
tests/test_qubo_spec_lowering.py
```

## Public Contract

The route emits:

```text
apc.qubo_lowering.v1
```

QUBO COO entries lower into CTIR energy metadata:

```text
qubo_coo
i
j
q
```

Linear terms are recorded in:

```text
objective.linear
ctir.linear_terms
```

Quadratic terms are recorded in:

```text
ctir.quadratic_terms
i
j
weight
```

## Execution Boundary

QUBO execution is not implemented in the CPU reference runtime yet. Lowering
reports therefore keep:

```text
execution_status: planned
```

Unsupported QUBO fields return:

```text
status: failed
reason
```

## Verification

Targeted tests cover:

```text
public QUBO spec validation
CTIR QUBO COO serialization
explicit linear and quadratic term reports
layout exposure of qubo.coo
structured unsupported-feature failure
planned execution boundary
```

## Next

Phase 54 should collect problem-family fixtures into one public fixture set.
