# Branch Tensor / Move Routes

`BranchTensor` makes repair routes explicit while preserving fixed tensor shape.

It is generated from:

```text
CTIRProblem
StatePool
```

Current route type:

```text
bit_flip(var_index)
```

Each route records:

```text
state_index
route_index
move_type
payload
canonical_key
```

The canonical key intentionally ignores the state index. That lets later phases
identify equivalent route types across candidate states without collapsing the
tensor shape.

Current API:

```text
branch_tensor_from_state_pool(problem, pool)
canonical_branch_keys(tensor)
mask_branch_tensor(tensor, alive_mask)
branch_tensor_summary(tensor)
```

Acceptance checks:

```text
BranchTensor shape is explicit.
Equivalent branches can be canonicalized.
Low-priority branches can be masked without changing tensor shape.
```
