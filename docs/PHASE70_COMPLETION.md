# Phase 70 Completion

Phase 70 implemented QUBO CUDA move scoring parity against the public QUBO CPU
reference route.

Deliverables completed:

```text
cuda/src/qubo_move_score.cu
cuda/include/apc_runtime.h
cuda/CMakeLists.txt
tests/cuda/test_qubo_move_score.py
docs/CUDA_OPERATOR_PARITY.md
docs/PHASE70_COMPLETION.md
```

Validation target:

```text
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair:. python3 -m unittest tests.cuda.test_qubo_move_score -v
```

The CUDA ABI records `bit_index`, `old_score`, `candidate_score`, and
`improves` for each state/bit move. The test skips cleanly without `nvcc` and
the public parity document makes no acceleration or solver-compatibility claim.
