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
ledger
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

The CPU route also emits deterministic ledger rows:

```text
iteration
best_penalty
unsatisfied_count
best_state
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

QUBO lowering remains available as an inspect-only report. The executable CPU
reference route is described below.

## QUBO CPU Reference Execution

The 0.3 CPU reference route is:

```python
from apc import QUBORuntimeConfig, describe_qubo_cpu_reference_execution_from_json

report = describe_qubo_cpu_reference_execution_from_json(
    "examples/specs/qubo_tiny.json",
    config=QUBORuntimeConfig(max_iters=4, batch_size=4, seed=2),
)
```

It emits:

```text
apc.qubo_cpu_reference_execution.v1
```

The route records:

```text
objective
penalty
energy
move_count
final_state
ledger
```

The QUBO route is deterministic under a fixed seed. It is CPU reference
evidence for later CUDA parity, not a solver-compatibility or performance
claim.

## QUBO CPU Reference Contract

The contract report remains available:

```python
from apc import describe_qubo_cpu_reference_contract_from_json

report = describe_qubo_cpu_reference_contract_from_json("examples/specs/qubo_tiny.json")
```

It emits:

```text
apc.qubo_cpu_reference_contract.v1
```

The contract records:

```text
runtime steps
operator names
status fields
ledger fields
call ledger shape
```

The contract now marks the QUBO CPU reference route as implemented. CUDA QUBO
parity remains gated on this CPU behavior and later evidence.

Unsupported QUBO fields return a structured lowering report with:

```text
status: failed
reason
```

## Fixture Set

The public fixture index is:

```text
examples/handoff/problem_family_fixtures.v1.json
```

It emits:

```text
apc.problem_family_fixture_index.v1
```

The index lists:

```text
binary_milp
maxsat
qubo
```

Each fixture records:

```text
name
family
spec
spec_schema
route_status
execution_status
command
evidence_paths
checked_report
```

Reproduce the index with:

```bash
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
```

Implemented routes include compact checked reports and public evidence paths.

## Boundary

The CPU reference path remains the behavioral baseline for implemented runtime
routes. MaxSAT is a small public runtime route. QUBO now has a deterministic CPU
reference execution route. The fixture set does not claim full solver coverage,
optimality proof, external solver compatibility, or accelerator comparison.
