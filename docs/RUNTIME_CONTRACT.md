# Runtime Contract

The runtime execution contract describes the public execution path before
heavier native host and CUDA work is added.

The contract is descriptive. It does not replace the CPU reference runtime and
does not change algorithm behavior.

## Schema

The default contract emits:

```text
schema: apc.runtime_execution_contract.v1
name
backend
problem_families
steps
non_goals
```

Each step records:

```text
name
kind
inputs
outputs
status
timing_fields
operator_name
notes
```

## Timing Fields

Runtime reports should keep timing fields explicit:

```text
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

Individual steps may use a subset, but every step must name the timing fields it
can report.

## Default CPU Runtime Path

The current public CPU repair contract uses:

```text
lower_problem_to_ctir
materialize_layouts
initialize_state_pool
initial_projection
eval_constraints
rectify_violations
reduce_penalty
record_metrics
reduce_best
generate_branch_tensor
score_branches
select_reduction_gate_actions
apply_selected_actions
project_public_summary
```

This describes the runtime path across:

```text
CTIR
layout materialization
operator registry
state pool
branch tensor
reduction gate
validation ledger
interface projection
```

## Public Use

Use the contract to inspect runtime boundaries:

```python
from apc.runtime_contract import describe_cpu_runtime_contract

report = describe_cpu_runtime_contract()
```

The report is JSON-ready and can be consumed by future host-runtime and CUDA
buildout work.

## Non-Goals

The runtime contract does not claim:

```text
full optimality proof
solver API replacement
performance improvement without complete timing evidence
stable adapter ABI
```

Future native host and CUDA code should implement this contract one step at a
time, with CPU reference behavior kept as the behavioral check.
