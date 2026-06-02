# Problem Families

Problem-family expansion keeps the runtime path from being tied to one tiny
binary MILP example.

## Current Families

```text
binary_milp
maxsat
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

## Boundary

The CPU reference path remains the behavioral baseline. The MaxSAT route is a
small public runtime route and does not claim full MaxSAT solver coverage,
optimality proof, or external solver compatibility.
