# Phase 60 Completion

Phase 60 added deterministic QUBO CPU reference execution.

Deliverables completed:

```text
src/apc/runtime_qubo_cpu.py
tests/test_qubo_cpu_reference.py
docs/PROBLEM_FAMILIES.md
```

Validation target:

```text
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair:. python3 -m unittest tests.test_qubo_cpu_reference tests.test_qubo_cpu_reference_contract -v
```

The route runs from `examples/specs/qubo_tiny.json`, evaluates QUBO energy,
scores deterministic bit-flip moves, records QUBO ledger rows, and keeps CUDA
QUBO parity gated on this CPU reference behavior.
