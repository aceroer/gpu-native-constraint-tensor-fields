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

Completion record:

```text
docs/PHASE30_COMPLETION.md
```

## Phase 31: Checked Handoff Fixture Archive

Archive a small checked handoff demo input/output pair for repeatable public
release evidence.

Deliverables:

```text
examples/handoff/
docs/RELEASE_NOTES_DRAFT.md
tests/test_checked_handoff_fixtures.py
```

Acceptance checks:

```text
Fixture source input uses vagent.apc_handoff_report.v1.
Fixture checked output uses apc.cross_project_handoff_check.v1.
Fixture output uses apc.checked_handoff_runtime_demo.v1.
Fixture route remains an inspection demo and avoids claiming runtime compatibility.
```

Completion record:

```text
docs/PHASE31_COMPLETION.md
```

## Phase 32: Fixture-Backed Release Evidence

Attach the checked handoff fixtures to release artifact collection.

Deliverables:

```text
scripts/collect_release_artifacts.py
docs/RELEASE_ARTIFACTS.md
tests/test_release_artifacts.py
```

Acceptance checks:

```text
Release artifacts name the handoff fixture input and outputs.
Collector checks that fixture schemas are present.
Release notes keep the fixture route bounded to inspection evidence.
```

Completion record:

```text
docs/PHASE32_COMPLETION.md
```

## Phase 33: Problem-Family Handoff Fixture

Add a slightly richer public handoff fixture tied to a named problem family.

Deliverables:

```text
examples/handoff/
docs/CHECKED_HANDOFF_DEMO.md
tests/test_problem_family_handoff_fixture.py
```

Acceptance checks:

```text
Fixture names a public problem family without adding a compatibility promise.
Checked report still emits apc.cross_project_handoff_check.v1.
Demo output still emits apc.checked_handoff_runtime_demo.v1.
Fixture route remains JSON-only.
```

Completion record:

```text
docs/PHASE33_COMPLETION.md
```

## Phase 34: Handoff Fixture Index

Add a compact public index for available handoff fixtures and schemas.

Deliverables:

```text
examples/handoff/README.md
docs/CHECKED_HANDOFF_DEMO.md
tests/test_handoff_fixture_index.py
```

Acceptance checks:

```text
Index names each fixture input, checked output, and demo output.
Index records source, checked, and demo schemas.
Index keeps all fixtures framed as inspection evidence, not compatibility.
```

Completion record:

```text
docs/PHASE34_COMPLETION.md
```

## Phase 35: Handoff Fixture Listing Helper

Add a small CLI helper that lists available handoff fixture sets.

Deliverables:

```text
scripts/list_handoff_fixtures.py
docs/CHECKED_HANDOFF_DEMO.md
tests/test_handoff_fixture_listing.py
```

Acceptance checks:

```text
Helper emits JSON with fixture names, file paths, schemas, and problem_family.
Helper reads repository fixtures only and does not import paired projects.
Helper frames fixture sets as inspection evidence, not compatibility.
```

Completion record:

```text
docs/PHASE35_COMPLETION.md
```

## Phase 36: Fixture Listing Release Evidence

Attach the handoff fixture listing helper to release evidence.

Deliverables:

```text
scripts/collect_release_artifacts.py
docs/RELEASE_ARTIFACTS.md
tests/test_release_artifacts.py
```

Acceptance checks:

```text
Release artifacts include apc.handoff_fixture_index.v1 evidence.
Collector checks the fixture index schema and status.
Release notes keep fixture listing scoped to public inspection evidence.
```

Completion record:

```text
docs/PHASE36_COMPLETION.md
```

## Phase 37: Release Evidence Reader

Add a small CLI helper that summarizes release artifact evidence.

Deliverables:

```text
scripts/inspect_release_artifacts.py
docs/RELEASE_ARTIFACTS.md
tests/test_release_artifact_reader.py
```

Acceptance checks:

```text
Reader consumes apc.release_artifacts.v1.
Reader reports release status, tag, commit, artifact schemas, and fixture count.
Reader keeps summary factual and avoids release-quality claims beyond evidence.
```

Completion record:

```text
docs/PHASE37_COMPLETION.md
```

## Phase 38: Release Evidence Smoke Command

Add one command route that runs the verifier, collector, and reader in order.

Deliverables:

```text
scripts/smoke_release_evidence.py
docs/RELEASE_ARTIFACTS.md
tests/test_release_evidence_smoke.py
```

Acceptance checks:

```text
Smoke command emits verifier, collector, and reader output paths.
Smoke command exits nonzero if any evidence step fails.
Smoke command keeps summaries factual and avoids release-quality claims beyond evidence.
```

Completion record:

```text
docs/PHASE38_COMPLETION.md
```

## Phase 39: 0.1.x Maintenance Tag Procedure

Add a compact procedure for maintenance tags after the first public release
evidence route is closed.

Deliverables:

```text
docs/MAINTENANCE_RELEASES.md
docs/RELEASE_ARTIFACTS.md
tests/test_maintenance_releases.py
```

Acceptance checks:

```text
Maintenance procedure references the smoke command.
Maintenance procedure names patch tag inputs and evidence outputs.
Maintenance procedure keeps release notes factual and avoids compatibility claims.
```

Completion record:

```text
docs/PHASE39_COMPLETION.md
```

## Phase 40: Runtime Execution Contract

Define the public execution contract between CTIR, layout materialization,
operators, state pools, branch routes, projections, and ledgers.

Deliverables:

```text
src/apc/runtime_contract.py
docs/RUNTIME_CONTRACT.md
tests/test_runtime_contract.py
```

Acceptance checks:

```text
Runtime steps have named inputs, outputs, status, and timing fields.
Runtime plans are JSON-ready.
The CPU runtime can be described without changing algorithm behavior.
The contract stays public and does not promise solver compatibility.
```

Completion record:

```text
docs/PHASE40_COMPLETION.md
```

## Phase 41: Operator Call Ledger

Record runtime contract step calls without changing runtime algorithm behavior.

Deliverables:

```text
src/apc/operator_call_ledger.py
docs/RUNTIME_CONTRACT.md
tests/test_operator_call_ledger.py
```

Acceptance checks:

```text
Call ledger rows name contract step, status, backend, and timing fields.
Call ledger rows are JSON-ready.
CPU runtime behavior remains unchanged when a call ledger is produced separately.
The ledger stays factual and avoids performance or compatibility claims.
```

Completion record:

```text
docs/PHASE41_COMPLETION.md
```

## Phase 42: Runtime Error and Status Codes

Add public status code records for runtime contract steps.

Deliverables:

```text
src/apc/runtime_status.py
docs/RUNTIME_CONTRACT.md
tests/test_runtime_status.py
```

Acceptance checks:

```text
Status codes are stable strings with public descriptions.
Runtime status records are JSON-ready.
Operator call ledger rows can reference status codes.
Status records stay factual and do not imply solver compatibility.
```

Completion record:

```text
docs/PHASE42_COMPLETION.md
```

## Phase 43: C++ Host ABI Header

Begin the optional C++ host runtime skeleton with a public ABI header.

Deliverables:

```text
native/include/apc_runtime.hpp
native/CMakeLists.txt
docs/RUNTIME_CONTRACT.md
tests/test_native_host_abi.py
```

Acceptance checks:

```text
Header names public status codes and operator call records.
Native build is optional and skips cleanly when no C++ toolchain is available.
Python tests can inspect the header text for public ABI fields.
The header mirrors public contracts without changing Python runtime behavior.
```

Completion record:

```text
docs/PHASE43_COMPLETION.md
```

## Phase 44: C++ CPU Operator Shim

Add a tiny optional C++ CPU operator shim behind the host ABI.

Deliverables:

```text
native/src/cpu_operator_shim.cpp
native/CMakeLists.txt
docs/RUNTIME_CONTRACT.md
tests/test_native_cpu_operator_shim.py
```

Acceptance checks:

```text
Shim exposes a small public function behind the host ABI.
Native build remains optional and skips cleanly without a C++ toolchain.
Python tests can build or inspect the shim without changing Python runtime behavior.
The shim remains a probe and does not claim solver compatibility.
```

Completion record:

```text
docs/PHASE44_COMPLETION.md
```

## Phase 45: Python Binding Probe

Add a small optional probe for the native host route from Python-facing tests.

Deliverables:

```text
scripts/probe_native_host.py
docs/RUNTIME_CONTRACT.md
tests/test_native_binding_probe.py
```

Acceptance checks:

```text
Probe reports whether the native host route can be configured or built.
Probe emits JSON-ready status and evidence paths.
Probe skips cleanly without CMake or a C++ toolchain.
Probe remains optional and does not change Python runtime behavior.
```

Completion record:

```text
docs/PHASE45_COMPLETION.md
```

## Phase 46: Linear CSR CUDA Parity

Start CUDA operator parity with the linear CSR evaluation operator.

Deliverables:

```text
cuda/src/linear_csr_eval.cu
tests/cuda/test_linear_csr_eval.py
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance checks:

```text
Linear CSR CUDA output matches CPU reference on small cases.
CUDA test skips cleanly without nvcc or a CUDA device.
Parity report keeps tolerance and timing fields explicit.
No speedup claim is emitted.
```

Completion record:

```text
docs/PHASE46_COMPLETION.md
```

## Phase 47: Projection CUDA Parity

Record CUDA parity evidence for binary projection.

Deliverables:

```text
cuda/src/projection.cu
tests/cuda/test_projection.py
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance checks:

```text
Projection CUDA output matches CPU binary projection behavior.
CUDA test skips cleanly without nvcc or a CUDA device.
Parity report keeps domain invariant and timing fields explicit.
No speedup claim is emitted.
```

Completion record:

```text
docs/PHASE47_COMPLETION.md
```

## Phase 48: Penalty Reduction CUDA Parity

Record CUDA parity evidence for weighted penalty reduction.

Deliverables:

```text
cuda/src/violation_reduce.cu
tests/cuda/test_penalty_reduce.py
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance checks:

```text
Penalty reduction CUDA output matches CPU weighted penalty behavior.
CUDA test skips cleanly without nvcc or a CUDA device.
Parity report keeps tolerance and timing fields explicit.
No speedup claim is emitted.
```

Completion record:

```text
docs/PHASE48_COMPLETION.md
```

## Phase 49: Benchmark Sweep Config

Add checked JSON-ready benchmark sweep configuration.

Deliverables:

```text
benchmarks/sweeps/
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep.py
```

Acceptance checks:

```text
Sweep configs name problem specs, backend, max_iters, and output paths.
Sweep configs are JSON-ready and validated.
Sweep docs keep timing fields explicit.
Sweep docs avoid speedup claims without complete timing evidence.
```

Completion record:

```text
docs/PHASE49_COMPLETION.md
```

## Phase 50: Benchmark Sweep Runner

Add a runner that consumes benchmark sweep configs.

Deliverables:

```text
scripts/run_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep_runner.py
```

Acceptance checks:

```text
Runner consumes apc.benchmark_sweep_config.v1.
Runner writes per-case benchmark reports and a JSON-ready sweep summary.
Runner keeps CUDA unavailable behavior factual.
Runner avoids speedup claims without complete timing evidence.
```

Completion record:

```text
docs/PHASE50_COMPLETION.md
```

## Phase 51: Benchmark Sweep Report

Add a compact reader for benchmark sweep summaries.

Deliverables:

```text
scripts/inspect_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep_report.py
```

Acceptance checks:

```text
Report reader consumes apc.benchmark_sweep.v1.
Report reader lists case statuses, output paths, backends, and timing fields.
Report reader keeps unavailable CUDA factual.
Report reader avoids speedup claims without complete timing evidence.
```

Completion record:

```text
docs/PHASE51_COMPLETION.md
```

## Phase 52: MaxSAT Runtime Route

Add a small MaxSAT route through the public runtime path.

Deliverables:

```text
src/apc/readings/maxsat.py
examples/specs/maxsat_tiny.json
docs/PROBLEM_FAMILIES.md
tests/test_maxsat_runtime_route.py
```

Acceptance checks:

```text
MaxSAT example lowers through the existing public runtime contract.
Weighted soft clauses record objective contributions explicitly.
Hard clause violations record penalty contributions explicitly.
Unsupported MaxSAT features fail with structured status.
The CPU reference path remains the behavioral baseline.
```

Completion record:

```text
docs/PHASE52_COMPLETION.md
```

## Phase 53: QUBO Spec and Lowering

Add a small QUBO spec and CTIR lowering route.

Deliverables:

```text
src/apc/readings/qubo.py
examples/specs/qubo_tiny.json
docs/PROBLEM_FAMILIES.md
tests/test_qubo_spec_lowering.py
```

Acceptance checks:

```text
QUBO example validates as a public problem-family spec.
QUBO COO entries lower into CTIR energy view metadata.
Linear and quadratic terms are recorded explicitly.
Unsupported QUBO features fail with structured status.
The CPU reference path remains separate from unimplemented QUBO execution.
```

Completion record:

```text
docs/PHASE53_COMPLETION.md
```

## Phase 54: Problem-Family Fixture Set

Collect small public fixtures for implemented and planned problem-family routes.

Deliverables:

```text
examples/specs/
examples/handoff/
docs/PROBLEM_FAMILIES.md
tests/test_problem_family_fixture_set.py
```

Acceptance checks:

```text
Binary MILP, MaxSAT, and QUBO fixtures are listed in one JSON-ready index.
Fixture records name schema, family, route status, and public command surface.
Implemented routes include checked runtime or lowering reports.
Planned execution routes remain marked as planned.
Fixture docs avoid solver compatibility or performance claims.
```

Completion record:

```text
docs/PHASE54_COMPLETION.md
```

## Phase 55: 0.2 Release Checklist

Add the public checklist for the 0.2 Native Runtime Buildout release.

Deliverables:

```text
docs/RELEASE_CHECKLIST_0_2.md
docs/RELEASE_NOTES_0_2_DRAFT.md
tests/test_release_checklist_0_2.py
```

Acceptance checks:

```text
Checklist names the required verifier, artifact collector, and smoke commands.
Checklist includes runtime contract, native host, CUDA parity, benchmark sweep, and problem-family fixture gates.
Release notes state limits and non-goals clearly.
Checklist avoids solver compatibility or performance claims without evidence.
```

Completion record:

```text
docs/PHASE55_COMPLETION.md
```

## Phase 56: 0.2 Artifact Collection

Collect and inspect 0.2 release candidate artifacts.

Deliverables:

```text
docs/RELEASE_ARTIFACTS.md
docs/RELEASE_ARCHIVE_0_2.md
tests/test_release_artifacts_0_2.py
```

Acceptance checks:

```text
0.2 artifact collection references verifier, collector, reader, and smoke outputs.
0.2 archive draft records candidate tag, commit field, and required evidence paths.
Artifact checks include 0.2 checklist, release notes, benchmark sweep, and problem-family fixture evidence.
Archive draft avoids tag-final claims before a checked public tag exists.
```

Completion record:

```text
docs/PHASE56_COMPLETION.md
```

## Phase 57: 0.2 Public Tag

Add the public 0.2 tag execution procedure.

Deliverables:

```text
docs/TAG_EXECUTION_0_2.md
docs/RELEASE_ARCHIVE_0_2.md
tests/test_tag_execution_0_2.py
```

Acceptance checks:

```text
Tag procedure requires full verifier, artifact collector, reader, and smoke success.
Tag procedure requires candidate commit to match artifact report commit.
Archive draft defines how to become a final archive after tag verification.
Procedure avoids claiming a published tag before the tag exists.
```

Completion record:

```text
docs/PHASE57_COMPLETION.md
```

## Phase 58: Post-0.2 Runtime Expansion Plan

Plan the next public runtime expansion after the 0.2 tag procedure.

Deliverables:

```text
docs/POST_0_2_RUNTIME_PLAN.md
docs/NEXT_MAJOR_STAGE.md
tests/test_post_0_2_runtime_plan.py
```

Acceptance checks:

```text
Plan names QUBO CPU reference execution as a gated future route.
Plan names broader CUDA parity only after CPU references exist.
Plan names benchmark and fixture expansion without performance claims.
Plan keeps public terminology and solver-compatibility boundaries visible.
```

Completion record:

```text
docs/PHASE58_COMPLETION.md
```

## Phase 59: QUBO CPU Reference Contract

Define the executable CPU reference contract for the QUBO runtime route.

Deliverables:

```text
docs/POST_0_2_RUNTIME_PLAN.md
src/apc/runtime_qubo_cpu.py
tests/test_qubo_cpu_reference_contract.py
```

Acceptance checks:

```text
Contract names QUBO runtime inputs, outputs, status fields, and ledger fields.
Contract requires deterministic CPU reference behavior before CUDA parity.
Contract keeps unsupported QUBO features explicit.
Contract avoids solver compatibility or performance claims.
```

Completion record:

```text
docs/PHASE59_COMPLETION.md
```

## Phase 60: QUBO CPU Execution Route

Implement the deterministic CPU reference route for tiny QUBO instances.

Deliverables:

```text
src/apc/runtime_qubo_cpu.py
tests/test_qubo_cpu_reference.py
docs/PROBLEM_FAMILIES.md
```

Acceptance checks:

```text
QUBO CPU reference execution runs from examples/specs/qubo_tiny.json.
Route records objective, energy, move count, final state, and ledger rows.
Route is deterministic under a fixed seed.
Route keeps CUDA parity as a later gated step.
```

Completion record:

```text
docs/PHASE60_COMPLETION.md
```

## Phase 61: QUBO Runtime Ledger Evidence

Package QUBO CPU runtime ledger evidence for later release and CUDA parity
comparison.

Deliverables:

```text
docs/PROBLEM_FAMILIES.md
docs/RELEASE_ARTIFACTS.md
tests/test_qubo_cpu_reference.py
```

Acceptance checks:

```text
QUBO runtime ledger rows are JSON-ready evidence.
QUBO execution report is included in release artifact planning.
Ledger evidence states CPU reference status without acceleration claims.
CUDA parity remains a later gated step.
```

Completion record:

```text
docs/PHASE61_COMPLETION.md
```

## Phase 62: MaxSAT CPU Reference Expansion

Expand the existing MaxSAT CPU route into the 0.3 reference-first runtime
sequence.

Deliverables:

```text
src/apc/readings/maxsat.py
tests/test_maxsat_runtime_route.py
docs/PROBLEM_FAMILIES.md
```

Acceptance checks:

```text
MaxSAT route emits deterministic ledger-ready evidence.
Unsupported MaxSAT inputs fail with structured status.
Route keeps native fixtures small and inspectable.
CUDA parity remains a later gated step.
```

Completion record:

```text
docs/PHASE62_COMPLETION.md
```

## Phase 63: CUDA Parity Target Selection

Choose the first CUDA parity targets from implemented CPU reference routes.

Deliverables:

```text
docs/CUDA_OPERATOR_PARITY.md
docs/POST_0_2_RUNTIME_PLAN.md
tests/cuda/
```

Acceptance checks:

```text
Each selected CUDA target names its CPU reference route.
QUBO and MaxSAT CUDA targets remain small smoke candidates.
CUDA tests skip cleanly without nvcc or a CUDA device.
No performance claim is made before complete timing evidence.
```

Completion record:

```text
docs/PHASE63_COMPLETION.md
```

## Phase 64: QUBO CUDA Parity Smoke

Add the first QUBO CUDA parity smoke target against the CPU reference route.

Deliverables:

```text
cuda/src/qubo_energy.cu
tests/cuda/test_qubo_energy.py
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance checks:

```text
QUBO CUDA energy evaluation matches CPU reference values on a tiny fixture.
CUDA test skips cleanly without nvcc or a CUDA device.
Timing fields are factual if measured.
No acceleration claim is made.
```

Completion record:

```text
docs/PHASE64_COMPLETION.md
```

## Phase 65: MaxSAT CUDA Parity Smoke

Promote MaxSAT clause evaluation into the 0.3 CUDA parity smoke path.

Deliverables:

```text
cuda/src/clause_eval.cu
tests/cuda/test_clause_eval.py
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance checks:

```text
MaxSAT CUDA clause evaluation matches CPU unsatisfied-clause indicators.
CUDA test skips cleanly without nvcc or a CUDA device.
The target remains operator-level, not full runtime coverage.
No acceleration claim is made.
```

Completion record:

```text
docs/PHASE65_COMPLETION.md
```

## Phase 66: Benchmark Sweep Expansion

Expand benchmark sweep evidence for implemented CPU and CUDA smoke routes.

Deliverables:

```text
benchmarks/sweeps/qubo_smoke.json
benchmarks/sweeps/maxsat_smoke.json
scripts/run_benchmark_sweep.py
scripts/inspect_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
```

Acceptance checks:

```text
Benchmark sweep reports include backend, family, status, and timing fields.
CUDA unavailable or skipped status remains explicit.
Sweep docs avoid acceleration claims.
Small fixtures remain quick to run.
```

Completion record:

```text
docs/PHASE66_COMPLETION.md
```

## Phase 67: Fixture Expansion

Expand public fixture metadata for 0.3 runtime and parity evidence.

Deliverables:

```text
examples/handoff/problem_family_fixtures.v1.json
scripts/list_problem_family_fixtures.py
docs/PROBLEM_FAMILIES.md
tests/test_problem_family_fixture_set.py
```

Acceptance checks:

```text
Each fixture names schema, route, status, and evidence path.
QUBO and MaxSAT fixtures point to runtime evidence.
CUDA parity fixtures remain public-only and claim no acceleration.
Fixture set stays small enough for quick local checks.
```

Completion record:

```text
docs/PHASE67_COMPLETION.md
```

## Phase 68: 0.3 Release Checklist

Prepare the 0.3 release evidence checklist and tag-readiness documents.

Deliverables:

```text
docs/RELEASE_CHECKLIST_0_3.md
docs/RELEASE_NOTES_0_3_DRAFT.md
docs/RELEASE_ARCHIVE_0_3.md
docs/TAG_EXECUTION_0_3.md
```

Acceptance checks:

```text
Checklist names full verifier, CUDA smoke, sweep reports, and boundary scan.
Release notes keep non-goals and unsupported routes visible.
Archive draft remains factual until a tag exists.
Tag execution doc records commands without claiming a tag early.
```

Completion record:

```text
docs/PHASE68_COMPLETION.md
```

## Phase 69: 0.4 Route Plan

Plan the next public runtime stage after the 0.3 reference-first runtime
expansion.

Deliverables:

```text
docs/POST_0_3_RUNTIME_PLAN.md
docs/PHASE69_COMPLETION.md
tests/test_post_0_3_runtime_plan.py
```

Acceptance checks:

```text
The 0.4 route is named Native Runtime Consolidation.
The route starts with QUBO CUDA move scoring parity.
CUDA work remains gated by CPU references and clean skip behavior.
Public docs keep no acceleration, solver-compatibility, or drop-in replacement claim.
The next phase is visible as Phase 70.
```

Completion record:

```text
docs/PHASE69_COMPLETION.md
```

## Phase 70: QUBO CUDA Move Scoring Parity

Implement the first 0.4 CUDA parity target against the QUBO CPU reference
route.

Deliverables:

```text
cuda/src/qubo_move_score.cu
cuda/include/apc_runtime.h
tests/cuda/test_qubo_move_score.py
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance checks:

```text
QUBO CUDA move scoring parity matches CPU reference values on tiny fixtures.
Each tested move records bit index, old score, candidate score, and improves.
CUDA test skips cleanly without nvcc or a CUDA device.
No acceleration claim is made.
```

Completion record:

```text
docs/PHASE70_COMPLETION.md
```

## Phase 71: CUDA Parity Report Integration

Add a public inspector for CUDA parity targets and CUDA environment status.

Deliverables:

```text
scripts/inspect_cuda_parity.py
tests/cuda/test_parity_report.py
docs/CUDA_OPERATOR_PARITY.md
```

Acceptance checks:

```text
Parity reports name operator, family, backend, reference route, and status.
Unavailable CUDA is recorded as unavailable, not hidden as success.
Timing fields separate kernel, copy, layout, and end-to-end durations when run.
The report remains useful on machines without CUDA.
```

Completion record:

```text
docs/PHASE71_COMPLETION.md
```

## Phase 72: Runtime CLI Family Routing

Expose implemented problem-family routes through one stable public CLI command.

Deliverables:

```text
src/apc/cli.py
docs/QUICKSTART.md
tests/test_cli.py
```

Acceptance checks:

```text
CLI routing can run binary_milp, qubo, and maxsat examples.
Each route emits schema, family, backend, status, and evidence fields.
Unsupported family names fail with structured status.
The command remains small enough for quick local smoke runs.
```

Completion record:

```text
docs/PHASE72_COMPLETION.md
```

## Phase 73: Run Artifact Writer

Add stable runtime artifact directories for public evidence and debugging.

Deliverables:

```text
src/apc/run_artifacts.py
docs/RUNTIME_CONTRACT.md
tests/test_run_artifacts.py
```

Acceptance checks:

```text
Run outputs have a stable directory layout.
Each run writes inputs, result, ledger, timings, and metadata.
Artifact files are JSON-ready and deterministic for tiny fixtures.
Temporary or local machine paths do not leak into public examples.
```

Completion record:

```text
docs/PHASE73_COMPLETION.md
```

## Phase 74: Native Host Bridge Consolidation

Consolidate the optional native host bridge around request, result, status, and
timing records.

Deliverables:

```text
native/include/apc_runtime.hpp
native/src/cpu_operator_shim.cpp
docs/RUNTIME_CONTRACT.md
tests/test_native_host_abi.py
tests/test_native_cpu_operator_shim.py
```

Acceptance checks:

```text
Native host bridge names status, operator request, operator result, and timings.
Optional native builds skip cleanly when the toolchain is unavailable.
Python CPU references remain the source of expected values.
The bridge does not promise a stable external ABI before a checked adapter exists.
```

Completion record:

```text
docs/PHASE74_COMPLETION.md
```

## Phase 75: Benchmark Timing Expansion

Expand benchmark timing evidence across implemented public family routes.

Deliverables:

```text
benchmarks/sweeps/
scripts/run_benchmark_sweep.py
scripts/inspect_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep_report.py
```

Acceptance checks:

```text
Benchmark reports cover binary_milp, qubo, and maxsat smoke fixtures.
Reports include backend, family, operator, status, and timing fields.
CUDA unavailable status remains explicit on non-CUDA machines.
Docs avoid performance claims without complete timing evidence.
```

Completion record:

```text
docs/PHASE75_COMPLETION.md
```

## Phase 76: Contributor Extension Guide

Add a public guide for contributing new operators and problem families.

Deliverables:

```text
docs/CONTRIBUTING_OPERATORS.md
docs/PROBLEM_FAMILIES.md
examples/specs/
tests/test_contributing_operators.py
```

Acceptance checks:

```text
The guide shows the public order: spec, lowering, CPU reference, tests, optional CUDA.
It names required docs, fixture metadata, and release evidence touch points.
It avoids solver compatibility and performance promises.
It keeps examples small and inspectable.
```

Completion record:

```text
docs/PHASE76_COMPLETION.md
```

## Phase 77: Runtime Debug Tools

Add public debug reports for real-environment runtime failures.

Deliverables:

```text
src/apc/debug.py
scripts/inspect_runtime_debug.py
docs/DEBUGGING.md
tests/test_runtime_debug.py
```

Acceptance checks:

```text
Debug reports can inspect specs, lowered CTIR, layout summaries, ledgers, run artifacts, and status codes.
CUDA debug output records device availability, nvcc availability, selected arch, and skip reason.
Debug reports avoid local secrets and machine-specific paths in public examples.
Failure records include enough context to reproduce tiny fixture failures.
Every later version keeps an explicit debug-tooling checkpoint before release evidence.
```

Completion record:

```text
docs/PHASE77_COMPLETION.md
```

## Phase 78: 0.4 Release Checklist

Prepare 0.4 release readiness documents.

Deliverables:

```text
docs/RELEASE_CHECKLIST_0_4.md
docs/RELEASE_NOTES_0_4_DRAFT.md
docs/TAG_EXECUTION_0_4.md
tests/test_release_checklist_0_4.py
```

Acceptance checks:

```text
Checklist names full verifier, CUDA parity report, debug report, sweeps, and artifact collection.
Release notes keep non-goals and unsupported routes visible.
Tag execution doc records commands without claiming a tag early.
No performance or solver compatibility claim is made.
```

Completion record:

```text
docs/PHASE78_COMPLETION.md
```

## Phase 79: 0.4 Release Evidence Archive

Prepare the 0.4 candidate release archive and artifact references.

Deliverables:

```text
docs/RELEASE_ARCHIVE_0_4.md
docs/RELEASE_ARTIFACTS.md
tests/test_release_artifacts_0_4.py
```

Acceptance checks:

```text
Archive names verifier, CUDA parity, runtime debug, sweep, and artifact outputs.
Archive remains candidate-only until a tag exists and matches the artifact commit.
Release artifact collection tracks 0.4 docs and tests.
Public limits remain visible.
```

Completion record:

```text
docs/PHASE79_COMPLETION.md
```

## Next Major Stage: 0.4 Native Runtime Consolidation

After the 0.3 reference-first runtime expansion, the next major stage is
planned in:

```text
docs/POST_0_3_RUNTIME_PLAN.md
```

The stage assumes the project may need to be advanced by one maintainer for a
while. The route keeps each step small and testable:

```text
QUBO CUDA move scoring parity
-> CUDA parity report integration
-> runtime CLI family routing
-> run artifact writer
-> native host bridge consolidation
-> benchmark timing expansion
-> contributor extension guide
-> runtime debug tools
-> public 0.4 release evidence
```

Starting with 0.4, every later version should keep an explicit debug-tooling checkpoint
before release evidence. The project is moving toward real runtime conditions,
so failures must be inspectable through public reports rather than only through
ad hoc local reproduction.

## Non-Goals For Early Versions

```text
Full MIP optimality proof
Full CP-SAT propagation engine
Drop-in replacement for Gurobi, CPLEX, or OR-Tools
Complete compatibility with existing solver file formats
Large CUDA kernel bundles before CPU/GPU differential tests exist
```

## 0.4 Closure Step

The unified 0.4 verification pass is complete on the local Mac route and on a
remote Windows CUDA host. The remote pass exposed a useful split: CUDA operator
parity can pass while Windows orchestration still needs platform-specific
debugging.

The 0.4 beta real-environment split is captured in:

```text
docs/POST_0_4_BETA_PLAN.md
```

0.4 beta should keep the compute core on a TCC or headless CUDA lane where
available, and use Windows as an orchestration layer for task launch, environment
initialization, log collection, and artifact handoff.

The beta debug checkpoint is now part of `apc.runtime_debug_report.v1` as
`apc.runtime_debug_beta_checkpoint.v1`. The next concrete step is to generate
and inspect the 0.4 beta evidence package with compute mode, host role, host
compiler readiness, CUDA differential-test status, release artifact status, and
PCI/HAL boundary status included.

The longer target is lower than TCC: PCI/PCIe is the hardware contract, a GPU HAL
normalizes WDDM, TCC, and Linux kernel-device differences, and CUDAOS owns the
GPU device-control lane above that HAL. In that model the CPU-side OS mainly
enumerates PCI devices and orchestrates processes, while register-level and PCI
BAR-space facts become debug/evidence surfaces rather than ad hoc host behavior.
The public line should keep this at the reproducible CUDA/HAL evidence boundary.
If deeper GPU takeover becomes necessary, reserve it for a vendor-agreed
restricted hardware-control layer after the customer, GPU vendor, interface
permissions, and support responsibilities are settled. That path is about
controlled entry into sensitive vendor-facing surfaces, not simply commercial
packaging. Public artifact schemas and debug vocabulary should remain usable
without that layer.
