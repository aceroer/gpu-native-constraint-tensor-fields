# Problem Families

Problem-family expansion keeps the runtime path from being tied to one tiny
binary MILP example.

## Current Families

```text
binary_milp
maxsat
qubo
```

## MaxSAT Route

The first MaxSAT example is:

```text
examples/specs/maxsat_tiny.json
```

The public route is:

```python
from apc import run_maxsat_runtime_route_from_json

report = run_maxsat_runtime_route_from_json("examples/specs/maxsat_tiny.json")
```

It emits:

```text
apc.maxsat_runtime_route.v1
```

The route records:

```text
status
problem_family
backend
runtime_contract_schema
ctir
config
result
notes
```

Soft clauses report objective contributions:

```text
soft_objective_contributions
objective_contribution
```

Hard clauses report penalty contributions:

```text
hard_penalty_contributions
penalty_contribution
```

Unsupported MaxSAT fields return a structured route report with:

```text
status: failed
reason
```

## QUBO Lowering

The first QUBO example is:

```text
examples/specs/qubo_tiny.json
```

The public lowering route is:

```python
from apc import describe_qubo_lowering_from_json

report = describe_qubo_lowering_from_json("examples/specs/qubo_tiny.json")
```

It emits:

```text
apc.qubo_lowering.v1
```

The route records:

```text
status
problem_family
execution_status
ctir
config
notes
```

Linear terms are recorded in:

```text
ctir.linear_terms
```

Quadratic terms are recorded as COO-style entries:

```text
ctir.quadratic_terms
i
j
weight
```

QUBO execution is not implemented in the CPU reference runtime yet. The QUBO
route therefore reports:

```text
execution_status: planned
```

Unsupported QUBO fields return a structured lowering report with:

```text
status: failed
reason
```

## Boundary

The CPU reference path remains the behavioral baseline for implemented runtime
routes. MaxSAT is a small public runtime route. QUBO is currently a spec and
lowering route only. Neither route claims full solver coverage, optimality
proof, or external solver compatibility.
