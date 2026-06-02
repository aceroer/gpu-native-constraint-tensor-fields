# Examples

Examples are runnable from the repository root.

## Binary MILP Repair

```bash
cd examples/binary_milp_repair
PYTHONPATH=../../src:. python3 run_demo.py
```

This is the compact CPU reference repair loop.

## Vector-Native Repair

```bash
PYTHONPATH=src:examples/vector_state_repair python3 examples/vector_state_repair/run_demo.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo.json
```

This demo runs:

```text
CTIR
-> StatePool
-> BranchTensor
-> ReductionGate
-> InterfaceProjection
```

## Vector-Native Demo Benchmark

```bash
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo-bench.json
```

The benchmark output includes timing fields and keeps copy-time accounting
explicit.
