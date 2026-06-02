# GPU-Native Constraint Tensor Fields: Public Method Brief

Date: 2026-06-02

## 0. Scope

This project develops a GPU-native route for constraint optimization and feasibility repair.

The aim is not to port CPU branch-and-bound, backtracking, or propagation trees directly to GPU kernels. The aim is to reformulate constraint problems as batched tensor and sparse-operator workflows that fit GPU execution naturally.

Core pipeline:

```text
state batch
-> constraint response
-> residual / violation field
-> repair direction
-> projection
-> candidate selection
```

## 1. Problem Form

The target problem family can be written as:

\[
x\in\Omega,\qquad C_i(x)\le 0,\qquad f(x)\to\min.
\]

This covers first-stage instances from:

```text
binary MILP feasibility repair
MaxSAT / weighted MaxSAT local improvement
QUBO / graph energy minimization
CP-SAT-style finite-domain repair
scheduling / routing / packing
```

The first implementation target should be a feasibility repair and primal-heuristic layer, not a full replacement for mature CPU solvers.

## 2. Method Objects

The public engineering objects are:

| Object | Role |
|---|---|
| StateBatch | batched candidate states |
| ConstraintData | sparse rows, clauses, edges, or finite-domain relations |
| ResponseBatch | raw constraint responses |
| ViolationBatch | nonnegative infeasibility tensor |
| ObjectiveBatch | objective values |
| MoveBatch | candidate local changes |
| Projection | map back into the valid domain |
| Metrics | objective, violation, incumbent, and runtime counters |

Typical shapes:

```python
X: int32[B, n]
V: float32[B, m] or compressed active violations
F: float32[B]
M: int32[B, K, move_dim]
```

## 3. Constraint Response

Each problem family supplies an evaluation operator.

For linear constraints:

\[
r=A x-b,\qquad v=\max(r,0).
\]

For clauses:

\[
v_j=\mathbf 1\{\text{clause }j\text{ is unsatisfied}\}.
\]

For QUBO:

\[
E(x)=x^\top Qx.
\]

The common abstraction is:

```python
response = evaluate_constraints(X, problem)
violation = positive_violation(response, problem)
penalty = reduce_violation(violation, weights)
energy = objective(X) + lambda_ * penalty
```

## 4. Repair Flow

A repair step proposes many candidate moves in parallel and scores them against the current violation field.

Examples:

```text
bit flip
integer step
variable reset
swap
segment reverse
rounding
destroy-repair
```

Generic loop:

```python
for t in range(max_iters):
    response = evaluate_constraints(X, problem)
    violation = positive_violation(response, problem)
    energy = compute_energy(X, violation, problem)
    incumbent = update_incumbent(incumbent, X, violation, energy)

    moves = propose_moves(X, violation, problem)
    scores = score_moves(X, moves, problem)
    chosen = select_moves(scores, violation)

    X = apply_moves(X, chosen)
    X = project_domain(X, problem.domains)
    X = diversify_if_stalled(X, energy)
```

## 5. CTIR Position

CTIR, the Constraint Tensor Intermediate Representation, is the execution-facing representation.

It should preserve enough structure to support multiple problem families while still mapping cleanly to sparse GPU layouts.

Initial CTIR components:

```text
VarDomain
LinearCSR
ClauseCSR
QUBOCOO
StateBatch
ViolationBatch
MoveBatch
```

The intended lowering path:

```text
problem object
-> CTIR
-> device layout
-> operator ABI
-> kernel specialization
-> runtime validation
```

## 6. Device Layouts

Recommended first layouts:

```text
CSR: sparse row evaluation for linear constraints
CSC: variable-centered delta updates
COO: QUBO / graph energy
Clause CSR: SAT / MaxSAT clause evaluation
candidate-major X[B, n]: natural for full candidate evaluation
variable-major X[n, B]: useful for variable-wise move scoring
```

The runtime may maintain multiple views when delta scoring and full evaluation need different access patterns.

## 7. Operator ABI

The low-level system should expose operators, not a monolithic solver API.

Core operators:

```text
eval_constraints
reduce_violations
generate_moves
score_moves
select_moves
apply_projection
reduce_best
record_metrics
```

This keeps the system extensible across MILP, MaxSAT, QUBO, and finite-domain repair.

## 8. First Kernel Group

The first custom-kernel group should stay small:

```text
binary state initialization
linear CSR constraint evaluation
positive-part violation reduction
bit-flip move delta scoring
binary projection
best-candidate reduction
```

These are enough to support a binary MILP or MaxSAT repair prototype.

## 9. Validation

Every GPU operator needs a CPU reference.

Validation requirements:

```text
small randomized instances
CPU/GPU differential tests
domain invariant checks
nonnegative violation checks
incumbent consistency checks
NaN/Inf checks
kernel timing
host-device copy timing
violation decay curves
feasible candidate count
```

The goal is to separate algorithmic improvement from data-transfer artifacts.

## 10. Public Positioning

Public description:

```text
GPU-native constraint tensor fields for feasibility repair and primal heuristics.
```

The project should be presented as a method for representing and executing constraint repair workflows through batched tensor fields, sparse layouts, projection operators, and differential validation.

