# Phase 49 Completion

Phase 49 added checked JSON-ready benchmark sweep configuration.

## Added

```text
src/apc/benchmark_sweep.py
benchmarks/sweeps/binary_milp_smoke.json
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep.py
```

## Sweep Config

The sweep config emits:

```text
apc.benchmark_sweep_config.v1
```

Each case records:

```text
problem spec
backend
max_iters
batch_size
seed
penalty_weight
output path
```

## Verification

Observed checks:

```text
tests/test_benchmark_sweep.py: OK
release evidence smoke command: ok
public boundary scan: empty
```

## Next Step

Phase 50 should add a benchmark sweep runner that consumes the config.
