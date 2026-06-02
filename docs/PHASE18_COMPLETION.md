# Phase 18 Completion

Phase 18 adds the vector-native repair demo bridge.

Implemented deliverables:

```text
examples/vector_state_repair/
docs/VECTOR_NATIVE_REPAIR_DEMO.md
tests/test_vector_state_repair_demo.py
```

Acceptance checks:

```text
Demo runs through StatePool, BranchTensor, ReductionGate, and InterfaceProjection.
Demo emits a reproducible report.
Report includes branch count, selected action count, and success signal.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests scripts examples/vector_state_repair
PYTHONPATH=src:examples/vector_state_repair python3 examples/vector_state_repair/run_demo.py --out /tmp/apc-vector-native-report.json
```

The next phase should connect the demo report into the benchmark harness.
