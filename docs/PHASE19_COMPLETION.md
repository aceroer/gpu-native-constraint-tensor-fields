# Phase 19 Completion

Phase 19 connects the vector-native demo to the benchmark harness.

Implemented deliverables:

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

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests scripts examples/vector_state_repair
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo-bench.json
```

The next phase should package the public examples into a compact release-ready
quickstart.
