# Windows sm_89 CUDA Benchmark Evidence

Date: 2026-06-02

This note records a successful CUDA timing probe on an Ada laptop GPU. It is a
CUDA availability and timing-accounting record, not a broad GPU speedup claim.

## Host

```text
host: DESKTOP-7BI8899
gpu: NVIDIA GeForce RTX 4070 Laptop GPU
driver: 595.79
nvidia_smi_cuda_version: 13.2
nvcc: 13.3.33
msvc: 19.50.35729.0
cuda_arch: sm_89
output: D:\codex_cuda_tests\apc-cuda-bench.json
```

## Command

```cmd
python scripts\run_cuda_bench.py examples\specs\binary_milp_tiny.json --out D:\codex_cuda_tests\apc-cuda-bench.json --element-count 16 --cuda-arch sm_89
```

## Result

```text
schema: apc.benchmark.v1
backend.available: true
config.cuda_arch: sm_89
copy_time_s: 0.000135168
kernel_time_s: 0.00046368
end_to_end_time_s: 2.8460894999998345
```

## Notes

The CUDA benchmark probe reports copy time and kernel time separately. It does
not emit a speedup ratio. Any later performance comparison should include
copy-time accounting and a reproducible CPU baseline.
