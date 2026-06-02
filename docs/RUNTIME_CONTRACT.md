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

## Operator Call Ledger

The operator call ledger records runtime contract step calls as factual rows:

```text
schema: apc.operator_call_ledger.v1
contract_schema
backend
rows
notes
```

Each row records:

```text
step_name
backend
status
timing
inputs
outputs
operator_name
```

Use it separately from the CPU runtime:

```python
from apc.operator_call_ledger import describe_contract_call_ledger
from apc.runtime_contract import default_runtime_execution_contract

contract = default_runtime_execution_contract()
ledger = describe_contract_call_ledger(contract)
```

The ledger can carry measured timing values when evidence exists. Empty timing
values remain explicit fields and should not be read as performance claims.

## Runtime Status Codes

Runtime status codes are stable public strings:

```text
implemented
planned
skipped
failed
unavailable
```

They are emitted as:

```text
schema: apc.runtime_status_codes.v1
codes
notes
```

Each code records:

```text
code
category
description
terminal
```

Operator call ledger rows use these status codes. `failed` marks a terminal
failure for an evidence run. `unavailable` records that a required backend or
device is not available.

## C++ Host ABI Header

The optional native host ABI begins with:

```text
native/include/apc_runtime.hpp
```

The header mirrors public records:

```text
apc.runtime_execution_contract.v1
apc.operator_call_ledger.v1
apc.runtime_status_codes.v1
```

It names:

```text
RuntimeStatus
RuntimeTiming
OperatorCallRecord
```

The first C++ CPU operator shim is:

```text
native/src/cpu_operator_shim.cpp
```

It exposes:

```text
make_probe_operator_call_record
native_probe_status
```

The shim is a host ABI probe. It records a public operator call shape and does
not execute solver logic.

The C++ host target is optional and should configure cleanly when disabled:

```bash
cmake -S native -B /tmp/apc-native-build -DAPC_ENABLE_NATIVE_HOST=OFF
```

## Native Host Probe

The Python-facing native host probe is:

```text
scripts/probe_native_host.py
```

It emits:

```text
schema: apc.native_host_probe.v1
status
reason
paths
steps
notes
```

Use it to collect optional configure/build evidence:

```bash
python3 scripts/probe_native_host.py --out /tmp/apc-native-host-probe.json
```

If CMake is unavailable, the probe returns `status: unavailable` and exits
cleanly. Failed configure or build steps return `status: failed`.

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
