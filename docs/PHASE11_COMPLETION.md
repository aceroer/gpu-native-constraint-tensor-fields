# Phase 11 Completion

Phase 11 adds CUDA benchmark timing reports.

Implemented deliverables:

```text
cuda/bench/
scripts/run_cuda_bench.py
tests/cuda/test_cuda_bench_report.py
src/apc/cuda_benchmark.py
docs/CUDA_BENCHMARK_TIMING.md
```

Acceptance checks:

```text
CUDA reports include kernel time and copy time separately.
CUDA benchmarks mark unavailable cleanly when nvcc or a CUDA device is unavailable.
CPU and CUDA benchmark reports share the same JSON schema.
No speedup ratio is emitted by CUDA-only reports.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-cuda-bench.json
PYTHONPATH=src python3 -m compileall src tests scripts
```

The next phase is layout materialization.
