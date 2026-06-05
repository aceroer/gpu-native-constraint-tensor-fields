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

## Weighted Penalty Reduction

The weighted penalty reduction parity target is:

```text
operator: reduce_penalty
cuda_symbols: apc_rectify_linear_violation, apc_reduce_weighted_penalty
cuda_source: cuda/src/violation_reduce.cu
cpu_reference: apc.operators_cpu.rectify_violations, apc.operators_cpu.reduce_penalty
test: tests/cuda/test_penalty_reduce.py
```

The penalty parity test builds a small CUDA harness when `nvcc` is available.
The harness:

```text
generates dense linear responses
computes CPU expected nonnegative violations in host code
computes CPU expected weighted penalties in host code
launches apc_rectify_linear_violation
launches apc_reduce_weighted_penalty
copies CUDA violations and penalties back to host
checks every violation is nonnegative
compares every violation and penalty with explicit tolerance
```

Tolerance:

```text
absolute_tolerance: 1e-9
```

Penalty invariant:

```text
violation_values: nonnegative
penalty_rule: sum(weight[row] * violation[row])
```

Timing fields for later parity reports:

```text
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

The current weighted penalty parity test is correctness-focused. It does not
emit a performance comparison.

## Skip Behavior

CUDA parity tests must skip cleanly when:

```text
nvcc is unavailable
a CUDA device is unavailable
CUDA build tools cannot compile the harness
```

When a specific device architecture is needed, set:

```bash
APC_CUDA_ARCH=sm_89 PYTHONPATH=src python3 -m unittest tests.cuda.test_linear_csr_eval tests.cuda.test_projection tests.cuda.test_penalty_reduce -v
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

## CUDA Parity Report

CUDA parity targets can be inspected with:

```bash
python3 scripts/inspect_cuda_parity.py --out /tmp/apc-cuda-parity-report.json
```

The report emits:

```text
schema: apc.cuda_parity_report.v1
operator, family, backend, reference route, and status
CUDA environment facts
target status and skip reason
timing fields
```

Unavailable CUDA is recorded as unavailable, not hidden as success. The report
is useful on machines without `nvcc` or without a CUDA device.

Report timing fields:

```text
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

## 0.3 CUDA Parity Target Selection

Phase 63 selects the first 0.3 CUDA parity targets from routes that already have
CPU reference behavior.

Selected targets:

```text
target_id: qubo_energy_eval
problem_family: qubo
operator: eval_qubo_energy
cpu_reference: apc.runtime_qubo_cpu.eval_qubo_energy
cuda_symbol: apc_eval_qubo_energy
cuda_source: cuda/src/qubo_energy.cu
test: tests/cuda/test_qubo_energy.py
status: implemented
planned_phase: Phase 64
```

```text
target_id: qubo_bitflip_score
problem_family: qubo
operator: score_qubo_bitflip_moves
cpu_reference: apc.runtime_qubo_cpu.score_qubo_bitflip_moves
cuda_symbol: apc_score_qubo_bitflip_moves
cuda_source: cuda/src/qubo_move_score.cu
test: tests/cuda/test_qubo_move_score.py
status: implemented
planned_phase: Phase 70
implemented_phase: Phase 70
```

```text
target_id: maxsat_clause_eval
problem_family: maxsat
operator: eval_unsatisfied_clauses
cpu_reference: apc.readings.maxsat.eval_unsatisfied_clauses
cuda_symbol: apc_eval_clause_csr
cuda_source: cuda/src/clause_eval.cu
test: tests/cuda/test_clause_eval.py
status: implemented
planned_phase: Phase 65
```

Selection gates:

```text
CPU reference route exists before CUDA parity.
CUDA target is a narrow operator, not a full solver route.
Small fixtures compare exact or tolerance-bound values.
CUDA tests skip cleanly without nvcc or a CUDA device.
Timing fields may be recorded, but no acceleration claim is made.
```

QUBO CUDA parity started with energy evaluation because it is the smallest
shared scalar evidence surface. QUBO move scoring now follows it as the first
0.4 CUDA parity target. MaxSAT clause evaluation already has a CUDA smoke path.

## QUBO Energy Evaluation

The QUBO energy parity target is:

```text
operator: eval_qubo_energy
cuda_symbol: apc_eval_qubo_energy
cuda_source: cuda/src/qubo_energy.cu
cpu_reference: apc.runtime_qubo_cpu.eval_qubo_energy
test: tests/cuda/test_qubo_energy.py
```

The QUBO energy parity test builds a small CUDA harness when `nvcc` is
available. The harness:

```text
loads tiny QUBO COO-style arrays
generates candidate-major binary states
computes CPU expected linear plus quadratic energy in host code
launches apc_eval_qubo_energy
copies CUDA energies back to host
compares every energy with explicit tolerance
```

The current QUBO energy parity test is correctness-focused. It does not emit a
performance comparison.

## QUBO Bitflip Move Scoring

The QUBO bitflip move-scoring parity target is:

```text
operator: score_qubo_bitflip_moves
cuda_symbol: apc_score_qubo_bitflip_moves
cuda_source: cuda/src/qubo_move_score.cu
cpu_reference: apc.runtime_qubo_cpu.score_qubo_bitflip_moves
test: tests/cuda/test_qubo_move_score.py
```

The QUBO move-scoring parity test builds a small CUDA harness when `nvcc` is
available. The harness:

```text
loads tiny QUBO COO-style arrays
generates candidate-major binary states
computes CPU expected current energy for each state
computes CPU expected post-flip energy for every state and bit index
launches apc_score_qubo_bitflip_moves
copies bit index, old score, candidate score, and improves values back to host
compares every output with explicit tolerance or exact integer equality
```

Move-score evidence shape:

```text
bit_index
old_score
candidate_score
improves
```

Tolerance:

```text
absolute_tolerance: 1e-9
```

The current QUBO move-scoring parity test is correctness-focused. It does not
emit a performance comparison.

Tolerance:

```text
absolute_tolerance: 1e-9
```

## MaxSAT Clause Evaluation

The MaxSAT clause parity target is:

```text
operator: eval_unsatisfied_clauses
cuda_symbol: apc_eval_clause_csr
cuda_source: cuda/src/clause_eval.cu
cpu_reference: apc.readings.maxsat.eval_unsatisfied_clauses
test: tests/cuda/test_clause_eval.py
status: implemented
```

The clause parity test builds a small CUDA harness when `nvcc` is available.
The harness:

```text
loads tiny clause CSR arrays
generates candidate-major binary states
computes CPU expected unsatisfied-clause indicators in host code
launches apc_eval_clause_csr
copies CUDA indicators back to host
checks every indicator exactly
```

Invariant:

```text
unsatisfied_indicator: 0_or_1
comparison: exact
```

## Next CUDA Parity Target

The next target is:

```text
operator: score_qubo_bitflip_moves
cuda_symbol: apc_score_qubo_bitflip_moves
cpu_reference: apc.runtime_qubo_cpu.score_qubo_bitflip_moves
planned_phase: Phase 64
```
