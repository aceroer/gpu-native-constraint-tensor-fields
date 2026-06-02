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

Completion record:

```text
docs/PHASE8_COMPLETION.md
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

Completion record:

```text
docs/PHASE9_COMPLETION.md
```

## Phase 10: Operator Registry

Make operator boundaries discoverable as data.

Deliverables:

```text
src/apc/operator_registry.py
docs/OPERATOR_REGISTRY.md
tests/test_operator_registry.py
```

Acceptance checks:

```text
Operators list required input and output layouts.
CPU reference functions are named explicitly.
CUDA ABI symbols are listed when available.
Registry summaries are printable from the CLI.
```

Completion record:

```text
docs/PHASE10_COMPLETION.md
```

## Phase 11: CUDA Benchmark Timing

Wire CUDA timing into the benchmark schema without hiding transfer overhead.

Deliverables:

```text
cuda/bench/
scripts/run_cuda_bench.py
tests/cuda/test_cuda_bench_report.py
```

Acceptance checks:

```text
CUDA reports include kernel time and copy time separately.
CUDA benchmarks skip cleanly when nvcc or a CUDA device is unavailable.
CPU and CUDA benchmark reports share the same JSON schema.
No speedup ratio is emitted unless both reports include copy time.
```

Completion record:

```text
docs/PHASE11_COMPLETION.md
```

## Phase 12: Layout Materialization

Turn layout plans into materialized host/device buffers.

Deliverables:

```text
src/apc/layout_materialize.py
tests/test_layout_materialize.py
docs/LAYOUT_MATERIALIZATION.md
```

Acceptance checks:

```text
Candidate-major to variable-major conversion is deterministic.
CSR to CSC conversion preserves all nonzeros.
Conversion cost ledger matches materialized element counts.
```

Completion record:

```text
docs/PHASE12_COMPLETION.md
```

## Phase 13: Compatibility Adapters

Add narrow adapters only after the native path remains stable.

Deliverables:

```text
src/apc/adapters/
docs/ADAPTERS.md
tests/test_adapters.py
```

Acceptance checks:

```text
Adapters lower into native specs or CTIR.
Adapters do not bypass layout planning or operator registry.
Unsupported solver features fail loudly.
```

Completion record:

```text
docs/PHASE13_COMPLETION.md
```

## Phase 14: State Pool Runtime

Make candidate batches first-class runtime state pools.

```text
src/apc/state_pool.py
docs/STATE_POOL.md
tests/test_state_pool.py
```

Acceptance checks:

```text
StatePool can initialize from CTIR.
StatePool records batch score and alive mask.
StatePool exports a JSON-ready summary.
```

Completion record:

```text
docs/PHASE14_COMPLETION.md
```

## Phase 15: Branch Tensor / Move Routes

Turn move batches into explicit branch tensors.

Deliverables:

```text
src/apc/branch_tensor.py
docs/BRANCH_TENSOR.md
tests/test_branch_tensor.py
```

Acceptance checks:

```text
BranchTensor shape is explicit.
Equivalent branches can be canonicalized.
Low-priority branches can be masked without changing tensor shape.
```

Completion record:

```text
docs/PHASE15_COMPLETION.md
```

## Phase 16: Reduction Gate

Select external actions from branch tensors deterministically.

Deliverables:

```text
src/apc/reduction_gate.py
docs/REDUCTION_GATE.md
tests/test_reduction_gate.py
```

Acceptance checks:

```text
Top-k filtering is reproducible.
Diversity penalty can be recorded.
Selected actions can be summarized for the ledger.
```

Completion record:

```text
docs/PHASE16_COMPLETION.md
```

## Phase 17: Interface Projection

Project native runtime state into public output forms.

Deliverables:

```text
src/apc/interface_projection.py
docs/INTERFACE_PROJECTION.md
tests/test_interface_projection.py
```

Acceptance checks:

```text
Runtime state is not treated as the public API shape.
Each public output includes a projection reason.
Adapters and summaries use projection helpers.
```

Completion record:

```text
docs/PHASE17_COMPLETION.md
```

## Phase 18: Vector-Native Repair Demo Bridge

Show the state-pool path as a public runnable demo.

Deliverables:

```text
examples/vector_state_repair/
docs/VECTOR_NATIVE_REPAIR_DEMO.md
tests/test_vector_state_repair_demo.py
```

Acceptance checks:

```text
Demo runs through StatePool, BranchTensor, ReductionGate, and InterfaceProjection.
Demo emits a reproducible report.
Report includes branch count, selected action count, and success signal.
```

Completion record:

```text
docs/PHASE18_COMPLETION.md
```

## Phase 19: Demo Benchmark Integration

Connect vector-native demo reports to the benchmark harness.

Deliverables:

```text
scripts/run_vector_demo_bench.py
benchmarks/vector_native_report.example.json
tests/test_vector_demo_benchmark.py
```

Acceptance checks:

```text
Benchmark script writes a projected JSON report.
Report includes runtime path metrics and benchmark timing fields.
No speedup claim is emitted without copy-time accounting.
```

Completion record:

```text
docs/PHASE19_COMPLETION.md
```

## Phase 20: Public Quickstart Packaging

Package the public examples into a compact first-run path.

Deliverables:

```text
docs/QUICKSTART.md
examples/README.md
benchmarks/README.md
```

Acceptance checks:

```text
Quickstart covers validate, run, benchmark, and vector-native demo benchmark.
Commands are copy-paste runnable from the repository root.
No internal-only terminology appears in public quickstart docs.
```

Completion record:

```text
docs/PHASE20_COMPLETION.md
```

## Phase 21: Public Handoff Checklist

Prepare the repo for outside contributors to inspect and extend.

Deliverables:

```text
docs/PUBLIC_HANDOFF.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_public_docs.py
```

Acceptance checks:

```text
Handoff document names stable entry points and next extension areas.
Release notes summarize public phases without internal-only terminology.
Public docs pass terminology boundary checks.
```

Completion record:

```text
docs/PHASE21_COMPLETION.md
```

## Phase 22: Release Verification Script

Collect the public verification commands into one script.

Deliverables:

```text
scripts/verify_public_release.py
docs/VERIFY_RELEASE.md
tests/test_release_verifier.py
```

Acceptance checks:

```text
Verifier runs tests, compileall, quickstart smoke commands, and boundary scan.
Verifier emits a JSON-ready result summary.
Verifier exits nonzero on failed command.
```

Completion record:

```text
docs/PHASE22_COMPLETION.md
```

## Phase 23: Release Tag Checklist

Prepare a small tag-ready release checklist.

Deliverables:

```text
docs/RELEASE_CHECKLIST.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_release_checklist.py
```

Acceptance checks:

```text
Checklist references the release verifier.
Checklist names tag, docs, tests, and benchmark artifacts.
Release notes remain public-only and current.
```

Completion record:

```text
docs/PHASE23_COMPLETION.md
```

## Phase 24: Release Artifact Normalization

Normalize tag evidence artifacts across verifier, benchmark, and release notes.

Deliverables:

```text
docs/RELEASE_ARTIFACTS.md
tests/test_release_artifacts.py
scripts/collect_release_artifacts.py
```

Acceptance checks:

```text
Artifact schema names verifier, benchmarks, docs, tests, and commit hash.
Collector emits JSON-ready release evidence.
Release notes reference the artifact contract.
```

Completion record:

```text
docs/PHASE24_COMPLETION.md
```

## Phase 25: First Public Tag Preparation

Prepare the first tag candidate after normalized release evidence exists.

Deliverables:

```text
docs/TAG_PREP.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_tag_prep.py
```

Acceptance checks:

```text
Tag prep references verifier and artifact collector outputs.
Release notes name the candidate tag and commit hash fields.
Tag prep keeps limits and non-goals visible.
```

Completion record:

```text
docs/PHASE25_COMPLETION.md
```

## Phase 26: First Public Tag Execution

Create the first public tag after Phase 25 evidence is clean.

Deliverables:

```text
docs/TAG_EXECUTION.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_tag_execution.py
```

Acceptance checks:

```text
Tag execution verifies the tag points to the collected commit hash.
Release notes record the final tag and evidence artifact paths.
Tag execution preserves the public language boundary.
```

Completion record:

```text
docs/PHASE26_COMPLETION.md
```

## Phase 27: Release Archive Handoff

Prepare a durable release archive handoff after the first public tag exists.

Deliverables:

```text
docs/RELEASE_ARCHIVE.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_release_archive.py
```

Acceptance checks:

```text
Archive doc names the tag, verifier, artifact report, and benchmark evidence.
Archive doc records how to reproduce the release evidence.
Release notes keep current limits and next work visible.
```

Completion record:

```text
docs/PHASE27_COMPLETION.md
```

## Phase 28: Cross-Project Handoff Sketch

Prepare a public sketch for connecting this release archive to the paired
vector-native runtime project.

Deliverables:

```text
docs/CROSS_PROJECT_HANDOFF.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_cross_project_handoff.py
```

Acceptance checks:

```text
Handoff sketch names the GPU release tag and artifact schema.
Handoff sketch names stable public entry points without private terminology.
Release notes describe the next cross-project route without claiming compatibility.
```

Completion record:

```text
docs/PHASE28_COMPLETION.md
```

## Phase 29: Public Adapter Sketch

Prepare a small public adapter consumer after the cross-project handoff exists.

Deliverables:

```text
src/apc/adapters/vagent_handoff.py
scripts/check_vagent_handoff.py
docs/RELEASE_NOTES_DRAFT.md
tests/test_vagent_handoff_consumer.py
```

Acceptance checks:

```text
Consumer validates vagent.apc_handoff_report.v1 JSON.
Consumer emits apc.cross_project_handoff_check.v1.
Consumer materializes StatePool, BranchTensor, ReductionGate, and InterfaceProjection public shapes.
Consumer remains a handoff check and avoids claiming stable adapter ABI.
```

Completion record:

```text
docs/PHASE29_COMPLETION.md
```

## Phase 30: Checked Handoff Runtime Route

Feed a checked handoff summary into a small GPU-side inspection or benchmark
route.

Deliverables:

```text
scripts/run_checked_handoff_demo.py
docs/RELEASE_NOTES_DRAFT.md
tests/test_checked_handoff_demo.py
```

Acceptance checks:

```text
Demo consumes apc.cross_project_handoff_check.v1.
Demo reports StatePool and selected action summaries.
Demo avoids claiming drop-in runtime compatibility.
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

The next concrete step is Phase 30: checked handoff runtime route.
