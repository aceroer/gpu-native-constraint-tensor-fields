# Phase 52 Completion

Phase 52 added the MaxSAT runtime route.

## Delivered

```text
src/apc/readings/maxsat.py
examples/specs/maxsat_tiny.json
docs/PROBLEM_FAMILIES.md
tests/test_maxsat_runtime_route.py
```

## Public Contract

The route emits:

```text
apc.maxsat_runtime_route.v1
```

It uses the existing runtime contract schema:

```text
apc.runtime_execution_contract.v1
```

## Contribution Records

Soft clauses record:

```text
soft_objective_contributions
objective_contribution
```

Hard clauses record:

```text
hard_penalty_contributions
penalty_contribution
```

Unsupported MaxSAT fields return:

```text
status: failed
reason
```

## Verification

Targeted route tests cover:

```text
CTIR lowering through the public route
soft objective contribution records
hard penalty contribution records
CPU reference baseline alignment
structured unsupported-feature failure
```

## Next

Phase 53 should add a small QUBO spec and lowering route.
