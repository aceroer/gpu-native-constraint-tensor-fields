# Handoff Fixtures

These fixtures are public JSON examples for the checked handoff route.

They are inspection evidence only. They are not a compatibility promise and do
not define a stable external runtime ABI.

## Schemas

```text
source report: vagent.apc_handoff_report.v1
checked report: apc.cross_project_handoff_check.v1
demo report: apc.checked_handoff_runtime_demo.v1
```

## Fixtures

### Generic Task-Pack Fixture

```text
source: vagent_apc_handoff_report.v1.json
checked: apc_handoff_check.v1.json
demo: apc_checked_handoff_demo.v1.json
problem_family: none
```

Reproduce:

```bash
PYTHONPATH=src python3 scripts/check_vagent_handoff.py examples/handoff/vagent_apc_handoff_report.v1.json --out /tmp/apc-handoff-check.json
PYTHONPATH=src python3 scripts/run_checked_handoff_demo.py /tmp/apc-handoff-check.json --out /tmp/apc-checked-handoff-demo.json
```

### Binary MILP Fixture

```text
source: vagent_binary_milp_handoff_report.v1.json
checked: apc_binary_milp_handoff_check.v1.json
demo: apc_binary_milp_checked_handoff_demo.v1.json
problem_family: binary_milp
```

Reproduce:

```bash
PYTHONPATH=src python3 scripts/check_vagent_handoff.py examples/handoff/vagent_binary_milp_handoff_report.v1.json --out /tmp/apc-binary-milp-handoff-check.json
PYTHONPATH=src python3 scripts/run_checked_handoff_demo.py /tmp/apc-binary-milp-handoff-check.json --out /tmp/apc-binary-milp-checked-handoff-demo.json
```

## Boundary

The fixtures stay JSON-only:

```text
No paired-project import.
No drop-in solver compatibility claim.
No stable adapter ABI claim.
No GPU speedup claim.
```
