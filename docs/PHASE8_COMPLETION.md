# Phase 8 Completion

Phase 8 adds weighted MaxSAT as the second public problem family.

Implemented deliverables:

```text
src/apc/readings/maxsat.py
examples/specs/maxsat_tiny.json
tests/test_maxsat_cpu.py
cuda/src/clause_eval.cu
tests/cuda/test_clause_eval.py
```

Implemented path:

```text
weighted MaxSAT JSON
-> MaxSATSpec
-> CTIR ClauseCSR
-> CPU unsatisfied clause indicators
-> CPU bit-flip repair
-> CUDA clause evaluation skeleton
```

Acceptance checks:

```text
Tiny weighted MaxSAT instances load and validate.
Unsatisfied clause indicators evaluate on CPU.
Weighted penalties reduce from unsatisfied indicators.
CPU bit-flip repair finds a zero-penalty assignment on the tiny example.
CUDA clause evaluation has a differential harness that runs when nvcc is available.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests
cmake -S cuda -B /tmp/apc-cuda-disabled -DAPC_ENABLE_CUDA=OFF
```

The repository is ready to move to Phase 9: benchmarks.
