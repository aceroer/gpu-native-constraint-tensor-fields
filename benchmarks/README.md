# Benchmarks

Benchmark commands are runnable from the repository root.

Benchmark JSON reports can be written here by:

```bash
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/latest.json
```

Vector-native demo benchmark reports can be written by:

```bash
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/vector_native_report.latest.json
```

Generated `*.json` files are runtime artifacts.
The checked-in `vector_native_report.example.json` file is a public schema example.

CUDA timing reports can be written by:

```bash
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/latest_cuda.json --element-count 16
```

If CUDA is unavailable, the report remains JSON and marks the backend unavailable.
