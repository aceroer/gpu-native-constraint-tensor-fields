# Benchmark Sweeps

Benchmark sweep configs define repeatable benchmark evidence inputs.

The first config is:

```text
benchmarks/sweeps/binary_milp_smoke.json
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

The sweep config and runner summary do not make performance claims. A
comparison layer must include complete timing evidence before making any
performance statement.
