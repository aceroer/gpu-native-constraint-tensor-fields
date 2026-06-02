# Binary MILP Repair Example

This is a lightweight code example for the theory stack.

It shows how the method becomes code:

```text
L5 problem reading: binary MILP feasibility repair
L6 CTIR: BinaryDomain, LinearCSR, StateBatch, MoveBatch shape
L7 device layout: candidate-major state batch, LinearCSR rows
L8 operators: eval, violation, score, projection, best reduction
L9 validation: CPU reference, invariants, ledger checks
```

The Python code is a runnable CPU reference. The CUDA files under `cuda/` show
the intended ABI and kernel style; they are not compiled on machines without
NVIDIA CUDA.

## Run

From this directory:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests
```

Run the small demo:

```bash
PYTHONPATH=. python3 run_demo.py
```

## Example Problem

The tiny MILP is:

```text
minimize 2*x0 + x1 + 2*x2

x0 + x1 >= 1
x1 + x2 >= 1
x0 + x2 <= 1
x in {0,1}^3
```

The best feasible solution is:

```text
x = (0, 1, 0)
objective = 1
```

## CUDA Shape

CUDA is written as operator ABI, not as one large solver kernel:

```text
cuda/include/apc_runtime.h
cuda/src/binary_milp_kernels.cu
```

The current CUDA example includes:

```text
apc_eval_linear_csr
apc_rectify_linear_violation
apc_reduce_weighted_penalty
apc_project_binary
```

These correspond to the public pipeline:

```text
constraint response -> nonnegative violation -> penalty ledger -> projection
```

