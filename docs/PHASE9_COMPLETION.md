# Phase 9 Completion

Phase 9 adds a benchmark harness with JSON output.

Implemented deliverables:

```text
benchmarks/
scripts/run_bench.py
docs/BENCHMARKING.md
src/apc/benchmark.py
tests/test_benchmark.py
```

Acceptance checks:

```text
Benchmark output is JSON.
Ledger rows and violation decay are included for plotting.
CPU and CUDA backends are reported separately.
Reports do not claim GPU speedup without copy-time accounting.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-bench.json
PYTHONPATH=src python3 -m compileall src tests scripts
```

The repository has reached the public roadmap's benchmark phase.
