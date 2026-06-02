# Benchmarking

Benchmark reports separate algorithm behavior from transfer, kernel, layout,
and end-to-end timing fields.

Run the default CPU benchmark:

```bash
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/latest.json
```

Run the CUDA timing report:

```bash
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/latest_cuda.json
```

The output is JSON:

```text
schema
problem
backend
config
metrics
layout
ledger
notes
```

## Metrics

```text
best_objective
best_penalty
feasible_count
violation_decay
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

For CPU runs, `kernel_time_s` records CPU operator runtime for schema
compatibility. `copy_time_s` is zero because there is no host-device transfer.

CUDA benchmark reports are emitted as a separate backend. If CUDA is unavailable,
the report marks the backend as not available. The report must not claim GPU
speedup unless copy time is included.

## Ledger Plots

The benchmark ledger is JSON and can be plotted by any external tool. The
`violation_decay` metric is copied directly from ledger active violation counts
so plots do not need to reinterpret runtime rows.
