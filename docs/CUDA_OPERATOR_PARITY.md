# CUDA Operator Parity

CUDA operator parity records compare narrow CUDA operators against CPU reference
behavior on small cases.

The first parity target is:

```text
operator: eval_constraints
cuda_symbol: apc_eval_linear_csr
cuda_source: cuda/src/linear_csr_eval.cu
cpu_reference: apc.operators_cpu.eval_constraints
test: tests/cuda/test_linear_csr_eval.py
```

## Linear CSR Evaluation

The linear CSR parity test builds a small CUDA harness when `nvcc` is available.
The harness:

```text
generates small CSR rows
generates candidate-major binary states
computes CPU expected Ax responses in host code
launches apc_eval_linear_csr
copies CUDA responses back to host
compares every response with explicit tolerance
```

Tolerance:

```text
absolute_tolerance: 1e-9
```

Timing fields for later parity reports:

```text
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

The current linear CSR parity test is correctness-focused. It does not emit a
performance comparison.

## Binary Projection

The binary projection parity target is:

```text
operator: apply_projection
cuda_symbol: apc_project_binary
cuda_source: cuda/src/projection.cu
cpu_reference: apc.operators_cpu.apply_projection
test: tests/cuda/test_projection.py
```

The projection parity test builds a small CUDA harness when `nvcc` is available.
The harness:

```text
generates out-of-domain integer states
computes CPU expected binary projection in host code
launches apc_project_binary
copies CUDA states back to host
checks every projected value is in {0, 1}
checks every projected value matches the CPU projection rule
```

Domain invariant:

```text
projected_values: 0_or_1
projection_rule: x >= 1 -> 1, otherwise 0
```

Timing fields for later parity reports:

```text
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

The current binary projection parity test is correctness-focused. It does not
emit a performance comparison.

## Skip Behavior

CUDA parity tests must skip cleanly when:

```text
nvcc is unavailable
a CUDA device is unavailable
CUDA build tools cannot compile the harness
```

## Evidence Boundary

Parity evidence should state:

```text
operator name
CPU reference
CUDA symbol
tolerance
input shape
status
timing fields when measured
```

Parity evidence should not state:

```text
GPU acceleration claim
solver compatibility claim
full runtime coverage claim
```

## Next CUDA Parity Target

The next target is:

```text
operator: reduce_penalty
cuda_symbol: apc_reduce_weighted_penalty
test: tests/cuda/test_penalty_reduce.py
```
