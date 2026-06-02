# Operator Registry

The operator registry is the public table of runtime boundaries.

It records:

```text
operator name
backend
required input layouts
output layouts
CPU reference function
CUDA ABI symbol when available
implementation status
```

Print it from the CLI:

```bash
PYTHONPATH=src python3 -m apc.cli operators
```

The registry is intentionally separate from layout planning. Layout planning
describes the tensors a CTIR problem needs; the registry describes the operator
boundaries that may consume those tensors.

The current registry covers:

```text
linear CSR evaluation
linear violation rectification
weighted penalty reduction
clause CSR evaluation
move generation and scoring
projection
best-candidate reduction
metrics recording
```
