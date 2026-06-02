# Vector-Native Repair Demo

This demo runs the public state-pool path:

```text
native problem spec
-> CTIR
-> StatePool
-> BranchTensor
-> ReductionGate
-> InterfaceProjection
```

Run:

```bash
PYTHONPATH=src:examples/vector_state_repair python3 examples/vector_state_repair/run_demo.py
```

The output is a projected JSON report:

```text
projection
payload
```

The payload includes:

```text
branch_count
selected_action_count
success
```
