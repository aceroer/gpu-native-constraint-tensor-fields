# Phase 6 Completion

Phase 6 adds CPU/GPU differential validation tests for the CUDA operator ABI.

Implemented deliverables:

```text
tests/cuda/test_linear_csr_eval.py
tests/cuda/test_projection.py
tests/cuda/test_penalty_reduce.py
tests/cuda/cuda_diff_utils.py
```

Differential coverage:

```text
apc_eval_linear_csr compares GPU responses against CPU-computed CSR responses.
apc_rectify_linear_violation checks nonnegative violations against CPU values.
apc_reduce_weighted_penalty compares weighted reductions against CPU values.
apc_project_binary checks projection values and binary domain invariants.
```

Acceptance checks:

```text
Deterministic random small CSR instances are checked with explicit tolerance.
Violation values are asserted nonnegative.
Projection keeps all states in the binary domain.
CUDA tests skip cleanly when nvcc is unavailable.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests
```

The repository is ready to move to Phase 7: device layout planner.
