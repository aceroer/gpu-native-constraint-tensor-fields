# CUDA Example Layer

This directory is a CUDA writing guide for the lightweight binary MILP repair example.

It is organized by operator, not by a monolithic solver:

```text
apc_eval_linear_csr          relation-field reading
apc_rectify_linear_violation nonnegative violation boundary
apc_reduce_weighted_penalty  ledger reduction
apc_project_binary           projection closure
```

The important method rule is:

```text
problem reading -> CTIR -> device layout -> operator ABI -> specialized kernel
```

## Files

```text
include/apc_runtime.h
src/binary_milp_kernels.cu
```

The repository-level optional build skeleton now lives at:

```text
../../../cuda/
```

Use that directory for compiled CUDA work. This example directory remains a
small, local guide for the binary MILP repair example.

## Notes

This machine may not have `nvcc`; the CPU reference in the parent directory is
the runnable validation anchor. When CUDA is available, this kernel file is the
starting point for a small compiled runtime.

Production extensions should add:

```text
CUB reductions
CSC / incidence lists for bit-flip deltas
row-length bucketization
CUDA event timing
host-device copy ledger
CPU/GPU differential tests
```
