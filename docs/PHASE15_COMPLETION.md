# Phase 15 Completion

Phase 15 adds branch tensor / move route materialization.

Implemented deliverables:

```text
src/apc/branch_tensor.py
tests/test_branch_tensor.py
docs/BRANCH_TENSOR.md
```

Acceptance checks:

```text
BranchTensor shape is explicit.
Equivalent branches can be canonicalized.
Low-priority branches can be masked without changing tensor shape.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests scripts
```

The next phase is deterministic reduction gate.
