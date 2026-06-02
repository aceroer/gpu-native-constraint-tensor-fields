# Roadmap

This project is a research scaffold for a GPU-native constraint repair toolchain.

The goal is not to clone an existing MIP, SAT, or CP-SAT solver API. Compatibility
can be added where useful, but the primary design target is a compact native
workflow:

```text
problem spec
-> CTIR lowering
-> device layout planning
-> operator registry
-> repair runtime
-> validation ledger
-> benchmark harness
```

## Design Principles

1. Use a small native problem spec before adding compatibility adapters.
2. Keep CTIR explicit and inspectable.
3. Expose operator ABI rather than a monolithic solver API.
4. Keep every GPU operator paired with a CPU reference.
5. Separate kernel time, copy time, layout-conversion time, and end-to-end time.
6. Treat feasibility repair and primal heuristics as the first deliverable.

## Phase 0: Public Scaffold

Status: complete.

Deliverables:

```text
README.md
docs/PUBLIC_GPU_NATIVE_METHOD_BRIEF.md
CUDA_NATIVE_METHODOLOGY.md
examples/binary_milp_repair/
```

Acceptance checks:

```text
The public method is readable without private notes.
The binary MILP repair example runs on CPU.
The CUDA files demonstrate operator-style kernel boundaries.
No CUDA toolkit is required for the public scaffold.
```

Current verification:

```bash
cd examples/binary_milp_repair
PYTHONPATH=. python3 -m unittest discover -s tests
PYTHONPATH=. python3 run_demo.py
```

Completion record:

```text
docs/PHASE0_COMPLETION.md
```

## Phase 1: Native Problem Spec

Status: complete.

Build a small JSON or YAML problem format that can describe first-stage repair
instances without importing a traditional solver model.

Initial target:

```text
binary MILP feasibility repair
```

Example shape:

```json
{
  "domain": { "type": "binary", "n_vars": 3 },
  "objective": { "linear": [2.0, 1.0, 2.0] },
  "constraints": {
    "linear_csr": {
      "n_rows": 3,
      "row_ptr": [0, 2, 4, 6],
      "col_idx": [0, 1, 1, 2, 0, 2],
      "coeff": [1, 1, 1, 1, 1, 1],
      "rhs": [1, 1, 1],
      "sense": [">=", ">=", "<="],
      "weight": [1, 1, 1]
    }
  }
}
```

Deliverables:

```text
src/apc/spec.py
src/apc/io_json.py
examples/specs/binary_milp_tiny.json
tests/test_spec_loading.py
```

Acceptance checks:

```text
Load a JSON spec into typed Python objects.
Reject malformed CSR structures.
Reject unsupported domain and row-sense values.
Round-trip one tiny spec without semantic loss.
```

Completion record:

```text
docs/PHASE1_COMPLETION.md
```

## Phase 2: CTIR Core

Status: complete.

Separate user-facing problem specs from execution-facing CTIR.

Deliverables:

```text
src/apc/ctir.py
src/apc/lowering.py
src/apc/inspect_ctir.py
```

CTIR objects:

```text
VarDomain
LinearCSR
ClauseCSR
QUBOCOO
StateBatch
ViolationBatch
MoveBatch
ProjectionSpec
LedgerSpec
```

Acceptance checks:

```text
Problem spec lowers into CTIR.
CTIR is serializable for inspection.
CTIR validation catches shape and index errors.
The existing binary MILP example uses CTIR, not ad hoc structures.
```

Completion record:

```text
docs/PHASE2_COMPLETION.md
```

## Phase 3: CPU Operator Runtime

Build a CPU reference runtime that uses the same operator boundaries intended for
CUDA.

Operators:

```text
eval_constraints
rectify_violations
reduce_penalty
generate_moves
score_moves
select_moves
apply_moves
apply_projection
reduce_best
record_metrics
```

Deliverables:

```text
src/apc/operators_cpu.py
src/apc/runtime_cpu.py
src/apc/ledger.py
tests/test_runtime_cpu.py
```

Acceptance checks:

```text
Run a full repair loop from JSON spec.
Record objective, penalty, feasible count, and active violations.
Keep binary domain invariants after projection.
Keep CPU reference deterministic under a fixed seed.
```

Completion record:

```text
docs/PHASE3_COMPLETION.md
```

## Phase 4: CLI

Create a small command line interface for the native workflow.

Commands:

```text
apc validate examples/specs/binary_milp_tiny.json
apc inspect-ctir examples/specs/binary_milp_tiny.json
apc run examples/specs/binary_milp_tiny.json --backend cpu
apc ledger runs/latest/ledger.json
```

Deliverables:

```text
src/apc/cli.py
pyproject.toml
```

Acceptance checks:

```text
CLI exits nonzero on invalid specs.
CLI prints a compact CTIR summary.
CLI run writes a ledger file.
CLI run reports best feasible candidate when found.
```

Completion record:

```text
docs/PHASE4_COMPLETION.md
```

## Phase 5: CUDA Build Skeleton

Turn the current CUDA sketch into a compilable optional runtime.

Deliverables:

```text
cuda/include/apc_runtime.h
cuda/src/linear_csr_eval.cu
cuda/src/violation_reduce.cu
cuda/src/projection.cu
cuda/CMakeLists.txt
```

Acceptance checks:

```text
Build succeeds when nvcc is available.
CUDA runtime can be disabled on machines without CUDA.
Header ABI stays operator-based.
Kernel launch wrappers expose status codes.
```

Completion record:

```text
docs/PHASE5_COMPLETION.md
```

## Phase 6: CPU/GPU Differential Validation

Add differential tests for every CUDA operator.

Deliverables:

```text
tests/cuda/test_linear_csr_eval.py
tests/cuda/test_projection.py
tests/cuda/test_penalty_reduce.py
```

Acceptance checks:

```text
Random small CSR instances match CPU response.
Violation values are nonnegative.
Projection keeps all states in domain.
Floating point comparisons use explicit tolerance.
CUDA tests skip cleanly when CUDA is unavailable.
```

Completion record:

```text
docs/PHASE6_COMPLETION.md
```

## Phase 7: Device Layout Planner

Introduce layout planning as a first-class step.

Layouts:

```text
candidate-major state batch
variable-major state batch
LinearCSR
LinearCSC / incidence list
ClauseCSR
QUBOCOO
active violation compaction
```

Deliverables:

```text
src/apc/layout.py
src/apc/layout_ledger.py
docs/DEVICE_LAYOUTS.md
```

Acceptance checks:

```text
Each operator declares required input and output layouts.
Layout conversion costs are recorded.
Dual views are explicit, not implicit.
Layout summaries are printable from the CLI.
```

Completion record:

```text
docs/PHASE7_COMPLETION.md
```

## Phase 8: MaxSAT Reading

Add the second problem family after binary MILP.

Deliverables:

```text
src/apc/readings/maxsat.py
examples/specs/maxsat_tiny.json
tests/test_maxsat_cpu.py
cuda/src/clause_eval.cu
```

Acceptance checks:

```text
Load a tiny weighted MaxSAT instance.
Evaluate unsatisfied clause indicators.
Run bit-flip repair on CPU.
Add CUDA clause evaluation when CUDA is available.
```

## Phase 9: Benchmarks

Create a benchmark harness that distinguishes algorithm behavior from transfer
and layout overhead.

Deliverables:

```text
benchmarks/
scripts/run_bench.py
docs/BENCHMARKING.md
```

Metrics:

```text
best objective
best penalty
feasible count
violation decay
kernel time
copy time
layout conversion time
end-to-end time
```

Acceptance checks:

```text
Benchmark output is JSON.
Plots can be generated from ledger files.
CPU and CUDA backends are reported separately.
No benchmark claims GPU speedup without copy-time accounting.
```

## Non-Goals For Early Versions

```text
Full MIP optimality proof
Full CP-SAT propagation engine
Drop-in replacement for Gurobi, CPLEX, or OR-Tools
Complete compatibility with existing solver file formats
Large CUDA kernel bundles before CPU/GPU differential tests exist
```

## Near-Term Next Step

The next concrete step is Phase 1:

```text
Add a native JSON spec and a loader for the existing binary MILP example.
```

This makes the library usable through a stable input format before expanding the
CUDA runtime.
