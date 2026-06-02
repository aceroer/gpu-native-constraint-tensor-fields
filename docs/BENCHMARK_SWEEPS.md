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
defer sweep execution to the runner phase
```

The sweep config does not make performance claims. A comparison layer must
include complete timing evidence before making any performance statement.
