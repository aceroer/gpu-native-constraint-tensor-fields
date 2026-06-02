# Phase 50 Completion

Phase 50 added the benchmark sweep runner.

## Delivered

```text
scripts/run_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep_runner.py
```

## Public Contract

The runner consumes:

```text
apc.benchmark_sweep_config.v1
```

It writes one per-case report:

```text
apc.benchmark.v1
```

It also emits a sweep summary:

```text
apc.benchmark_sweep.v1
```

## Case Statuses

```text
ok
unavailable
failed
```

CUDA unavailable behavior remains factual. A missing CUDA runtime is recorded as
`unavailable`, not as a benchmark comparison.

## Verification

Targeted runner tests cover:

```text
config consumption
per-case report output
JSON-ready sweep summary output
CUDA unavailable status recording
bad config rejection
```

## Next

Phase 51 should add a compact benchmark sweep report reader.
