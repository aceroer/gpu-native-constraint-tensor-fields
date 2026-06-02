# Checked Handoff Demo

This note describes the public Phase 30 route. It consumes the APC-side checked
handoff report emitted by `scripts/check_vagent_handoff.py` and produces a small
runtime inspection summary.

## Input

```text
schema: apc.cross_project_handoff_check.v1
producer: scripts/check_vagent_handoff.py
```

The demo intentionally consumes the checked report, not the original paired
project report. This keeps the route bounded to APC public shapes.

## Command

```bash
PYTHONPATH=src python3 scripts/check_vagent_handoff.py examples/handoff/vagent_apc_handoff_report.v1.json --out /tmp/apc-vagent-handoff-check.json
PYTHONPATH=src python3 scripts/run_checked_handoff_demo.py /tmp/apc-vagent-handoff-check.json --out /tmp/apc-checked-handoff-demo.json
```

The repository also carries fixed fixture outputs:

```text
examples/handoff/apc_handoff_check.v1.json
examples/handoff/apc_checked_handoff_demo.v1.json
```

## Output

```text
schema: apc.checked_handoff_runtime_demo.v1
source_schema: apc.cross_project_handoff_check.v1
runtime_route:
  checked handoff JSON
  StatePool inspection
  selected action summary
  InterfaceProjection payload
```

Each task summary records:

```text
task_id
StatePool batch and alive counts
BranchTensor shape and alive count
selected actions
branch efficiency
projection kind
```

## Boundary

This is an inspection demo. It is not a drop-in runtime compatibility claim and
does not import the paired project.
