# Device Layouts

Device layout planning is the step between CTIR and backend operators.

The planner makes layout decisions explicit:

```text
CTIR problem
-> layout views
-> operator input/output layout declarations
-> conversion cost ledger
-> backend runtime
```

## State Views

Candidate-major state batches are the primary state layout:

```text
state.candidate_major: X[batch_size, n_vars]
```

Variable-major state batches are declared as an explicit dual view:

```text
state.variable_major: X_t[n_vars, batch_size]
```

The dual view is not implicit. The planner records a conversion cost from
candidate-major to variable-major when a backend wants variable-local access.

## Sparse Linear Views

Linear constraints enter as CTIR CSR:

```text
linear.csr
```

The planner also declares a CSC / incidence dual view:

```text
linear.csc
```

This is used by move scoring and future delta kernels where variable incidence
is more important than row scans. The CSR-to-CSC conversion is recorded in the
layout cost ledger.

## Placeholder Views

The layout names for later problem families are reserved:

```text
clause.csr
qubo.coo
```

They are emitted only when the CTIR problem contains those views.

## Violation Views

Dense violations are the first runtime output:

```text
violation.dense: V[batch_size, n_constraints]
```

Active violation compaction is declared separately:

```text
violation.active_compact
```

The conversion cost is recorded as an upper bound because the final compacted
size is data-dependent.

## Operator Layouts

Every runtime operator declares required input and output layouts. For the
current binary MILP path:

```text
eval_constraints      state.candidate_major, linear.csr -> constraint.response_dense
rectify_violations    constraint.response_dense, linear.csr -> violation.dense
reduce_penalty        violation.dense, linear.csr -> ledger.dense
generate_moves        state.candidate_major -> move.bit_flip
score_moves           state.candidate_major, move.bit_flip, linear.csr, linear.csc -> move.score_dense
select_moves          move.score_dense -> move.selected
apply_moves           state.candidate_major, move.selected -> state.candidate_major
apply_projection      state.candidate_major -> state.candidate_major
reduce_best           state.candidate_major, ledger.dense -> best.candidate
record_metrics        ledger.dense, violation.active_compact -> validation.ledger
```

## CLI

Print the current layout plan:

```bash
PYTHONPATH=src python3 -m apc.cli layout examples/specs/binary_milp_tiny.json
```
