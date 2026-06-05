# Public Handoff

This repository is now ready for outside inspection and small extensions.

## Stable First-Run Path

Start here:

```text
docs/QUICKSTART.md
```

The quickstart covers:

```text
validate a native spec
run the CPU repair runtime
run the standard benchmark
run the vector-native repair demo
run the vector-native demo benchmark
run the optional CUDA timing probe
```

## Stable Entry Points

Core package modules:

```text
src/apc/spec.py
src/apc/lowering.py
src/apc/ctir.py
src/apc/layout.py
src/apc/operator_registry.py
src/apc/state_pool.py
src/apc/branch_tensor.py
src/apc/reduction_gate.py
src/apc/interface_projection.py
src/apc/runtime_contract.py
src/apc/operator_call_ledger.py
src/apc/runtime_status.py
src/apc/runtime_cpu.py
src/apc/benchmark.py
src/apc/readings/maxsat.py
src/apc/readings/qubo.py
native/include/apc_runtime.hpp
native/src/cpu_operator_shim.cpp
docs/CUDA_OPERATOR_PARITY.md
docs/BENCHMARK_SWEEPS.md
docs/PROBLEM_FAMILIES.md
docs/CONTRIBUTING_OPERATORS.md
docs/DEBUGGING.md
docs/RELEASE_CHECKLIST_0_2.md
docs/RELEASE_NOTES_0_2_DRAFT.md
docs/RELEASE_ARCHIVE_0_2.md
docs/TAG_EXECUTION_0_2.md
docs/POST_0_2_RUNTIME_PLAN.md
docs/POST_0_3_RUNTIME_PLAN.md
examples/handoff/problem_family_fixtures.v1.json
```

Runnable commands:

```text
python3 -m apc.cli validate
python3 -m apc.cli run
python3 scripts/run_bench.py
python3 scripts/run_cuda_bench.py
python3 examples/vector_state_repair/run_demo.py
python3 scripts/run_vector_demo_bench.py
python3 scripts/probe_native_host.py
python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-benchmark-sweep.json
python3 scripts/inspect_benchmark_sweep.py /tmp/apc-benchmark-sweep.json --out /tmp/apc-benchmark-sweep-summary.json
python3 scripts/inspect_runtime_debug.py examples/specs/qubo_tiny.json --out /tmp/apc-runtime-debug.json
PYTHONPATH=src python3 scripts/list_problem_family_fixtures.py --out /tmp/apc-problem-family-fixtures.json
```

## Extension Areas

Good first extensions:

```text
Add a new small native problem spec under examples/specs/.
Add a new CPU reference operator with tests.
Add a new branch route type and canonical key.
Add a runtime contract step with a test.
Add an operator call ledger row with a test.
Add a runtime status code with a test.
Add a native host ABI field with a test.
Add a native CPU shim probe with a test.
Add a native host probe field with a test.
Add a CUDA parity target with a CPU reference test.
Add a benchmark sweep config with a test.
Add a benchmark sweep runner check with a test.
Add a benchmark sweep reader check with a test.
Add a problem-family runtime route with a test.
Add a problem-family lowering route with a test.
Add a problem-family fixture record with a test.
Add a QUBO CPU reference execution route with a test.
Add more vector-native demo metrics.
Add a benchmark report example for a new problem family.
Add a runtime debug report for a real failure mode.
Follow docs/POST_0_3_RUNTIME_PLAN.md for 0.4 native runtime consolidation.
```

Larger extensions:

```text
Add QUBO/HUBO runtime support.
Add richer MaxSAT repair routes.
Add CUDA implementations behind existing CPU references.
Connect vector-native demo benchmark reports to longer benchmark sweeps.
Add debug tooling before broadening real-environment runtime coverage.
Follow docs/POST_0_2_RUNTIME_PLAN.md for reference-first runtime expansion.
Follow docs/POST_0_3_RUNTIME_PLAN.md for native runtime consolidation.
```

## Testing Expectations

Run:

```bash
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
```

For CUDA work, tests should continue to skip cleanly when `nvcc` is unavailable.

## Benchmark Expectations

Reports should keep timing fields explicit:

```text
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

Do not claim acceleration without copy-time accounting.

## Public Language Boundary

Public docs should use:

```text
GPU-native
constraint tensor field
state pool
branch tensor
reduction gate
interface projection
repair runtime
benchmark report
```

Avoid private research-system terms in public files.
