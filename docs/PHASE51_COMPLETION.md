# Phase 51 Completion

Phase 51 added the benchmark sweep reader.

## Delivered

```text
scripts/inspect_benchmark_sweep.py
docs/BENCHMARK_SWEEPS.md
tests/test_benchmark_sweep_report.py
```

## Public Contract

The reader consumes:

```text
apc.benchmark_sweep.v1
```

It emits:

```text
apc.benchmark_sweep_summary.v1
```

## Summary Fields

```text
source_schema
source_path
status
name
config_path
case_count
case_statuses
timing_fields
unavailable_cases
failed_cases
notes
```

The reader lists case status, backend, backend availability, backend reason,
spec path, output path, report schema, and timing fields.

## Verification

Targeted reader tests cover:

```text
summary parsing
case status listing
CUDA unavailable status preservation
unsupported schema handling
missing file handling
CLI summary output
```

## Next

Phase 52 should start problem-family expansion with a MaxSAT runtime route.
