# Benchmark Sweeps

Benchmark sweep configs define repeatable benchmark evidence inputs.

Current configs are:

```text
benchmarks/sweeps/binary_milp_smoke.json
benchmarks/sweeps/qubo_smoke.json
benchmarks/sweeps/maxsat_smoke.json
```

Schema:

```text
apc.benchmark_sweep_config.v1
```

Each case records:

```text
name
spec
backend
out
max_iters
batch_size
seed
penalty_weight
```

Required timing fields:

```text
kernel_time_s
copy_time_s
layout_conversion_time_s
end_to_end_time_s
```

Current sweep config purpose:

```text
define CPU and CUDA benchmark evidence inputs
cover binary_milp, qubo, and maxsat smoke families
keep output paths stable
keep benchmark controls explicit
feed the benchmark sweep runner
```

## Runner

Run the smoke sweep with:

```bash
python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-benchmark-sweep.json
```

The runner writes one `apc.benchmark.v1` report per case and a sweep summary:

```text
apc.benchmark_sweep.v1
```

Case statuses:

```text
ok
unavailable
failed
```

`unavailable` records a backend that could not run on the current machine. It
is not treated as a failed sweep case.

## Reader

Inspect a sweep summary with:

```bash
python3 scripts/inspect_benchmark_sweep.py /tmp/apc-benchmark-sweep.json --out /tmp/apc-benchmark-sweep-summary.json
```

The reader emits:

```text
apc.benchmark_sweep_summary.v1
```

The summary records:

```text
source_schema
source_path
status
name
config_path
case_count
case_statuses
operator
timing_fields
unavailable_cases
failed_cases
notes
```

Benchmark reports cover the `binary_milp`, `qubo`, and `maxsat` smoke fixtures.
Each sweep case records backend, family, operator, status, and timing fields.

The sweep config, runner summary, and reader summary do not make performance
claims. A comparison layer must include complete timing evidence before making
any performance statement.
