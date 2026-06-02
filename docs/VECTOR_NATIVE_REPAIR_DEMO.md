# Vector-Native Repair Demo Bridge

The demo bridge shows the public vector-native runtime path as a runnable report.

Pipeline:

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

Optional report output:

```bash
PYTHONPATH=src:examples/vector_state_repair python3 examples/vector_state_repair/run_demo.py --out benchmarks/vector_native_report.json
```

The report uses the same projection boundary as other public summaries:

```text
projection.kind
projection.reason
payload
```

Required metrics:

```text
branch_count
selected_action_count
success
```
