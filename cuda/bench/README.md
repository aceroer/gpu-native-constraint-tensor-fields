# CUDA Bench

`timing_probe.cu` is a minimal CUDA event timing probe used by:

```bash
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json
```

It reports host-device copy time and kernel time separately. It does not emit
speedup ratios.
