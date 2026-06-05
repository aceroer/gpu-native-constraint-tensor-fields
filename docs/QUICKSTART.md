# Quickstart

This quickstart is meant to run from the repository root.

## 1. Validate a Problem Spec

```bash
PYTHONPATH=src python3 -m apc.cli validate examples/specs/binary_milp_tiny.json
```

## 2. Run the CPU Repair Runtime

```bash
PYTHONPATH=src python3 -m apc.cli run examples/specs/binary_milp_tiny.json --max-iters 2 --ledger-out /tmp/apc-ledger.json
```

The command prints a JSON summary and writes a ledger file.

The same runtime command can route implemented public families:

```bash
PYTHONPATH=src python3 -m apc.cli run examples/specs/qubo_tiny.json --family auto --max-iters 2 --ledger-out /tmp/apc-qubo-report.json
PYTHONPATH=src python3 -m apc.cli run examples/specs/maxsat_tiny.json --family auto --max-iters 2 --ledger-out /tmp/apc-maxsat-report.json
```

Each route emits schema, family, backend, status, and evidence fields.

To write a stable artifact directory for a run:

```bash
PYTHONPATH=src python3 -m apc.cli run examples/specs/qubo_tiny.json --family auto --max-iters 2 --artifact-dir /tmp/apc-runs --run-id qubo_tiny
```

The run directory contains input, result, ledger, timings, and metadata JSON
files.

## 3. Run the Standard Benchmark

```bash
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-bench.json --max-iters 2
```

The report separates runtime timing fields and does not emit a speedup claim
without copy-time accounting.

## 4. Run the Vector-Native Demo

```bash
PYTHONPATH=src:examples/vector_state_repair python3 examples/vector_state_repair/run_demo.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo.json
```

The report is projected into:

```text
projection
payload
```

Required payload metrics:

```text
payload.metrics.branch_count
payload.metrics.selected_action_count
payload.metrics.success
```

## 5. Run the Vector-Native Demo Benchmark

```bash
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo-bench.json
```

The benchmark report includes:

```text
payload.benchmark.runtime_path
payload.benchmark.timing
payload.benchmark.notes
```

## 6. Optional CUDA Timing Probe

```bash
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-cuda-bench.json --element-count 16
```

On an Ada GPU, for example RTX 40-series, pass the architecture explicitly:

```bash
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-cuda-bench.json --element-count 16 --cuda-arch sm_89
```

Or set it once for CUDA benchmark and parity-test commands:

```bash
APC_CUDA_ARCH=sm_89 PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-cuda-bench.json --element-count 16
```

When `nvcc` or a CUDA device is unavailable, this command writes an unavailable
JSON report instead of claiming acceleration.

## 7. Inspect CUDA Parity Status

```bash
PYTHONPATH=src python3 scripts/inspect_cuda_parity.py --out /tmp/apc-cuda-parity-report.json
```

The report records CUDA target status, `nvcc` availability, device availability,
selected architecture, skip reason, and timing fields.
