# Reduction Gate

`ReductionGate` turns alive branch routes into selected external actions.

Inputs:

```text
CTIRProblem
StatePool
BranchTensor
```

The current gate scores each alive bit-flip route by post-route energy:

```text
energy = objective + penalty_weight * penalty
```

It then performs deterministic top-k selection. A diversity penalty can be
recorded for repeated canonical route keys:

```text
adjusted_energy = energy + diversity_penalty
```

Current API:

```text
ReductionConfig
reduce_branch_tensor(problem, pool, tensor)
reduction_gate_summary(result)
```

Acceptance checks:

```text
Top-k filtering is reproducible.
Diversity penalty can be recorded.
Selected actions can be summarized for the ledger.
```
