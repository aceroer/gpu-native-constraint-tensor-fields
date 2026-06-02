# CUDA Benchmark Timing

CUDA benchmark reports share the benchmark JSON schema used by CPU reports.

Run:

```bash
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/latest_cuda.json
```

For Ada GPUs, use:

```bash
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/latest_cuda.json --cuda-arch sm_89
```

When `nvcc` or a CUDA device is unavailable, the report is still JSON and marks
the CUDA backend as unavailable.

Timing fields:

```text
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

CUDA reports do not emit speedup ratios. A comparison layer must include copy
time before making any speedup claim.
