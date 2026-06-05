# 0.4 Release Checklist

0.4 is the Native Runtime Consolidation release candidate.

## Required Commands

Run from the repository root:

```bash
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair:. python3 -m unittest discover -s tests -v
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full-0-4.json
python3 scripts/inspect_cuda_parity.py --out /tmp/apc-cuda-parity-report-0-4.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/binary_milp_smoke.json --out /tmp/apc-binary-milp-sweep-0-4.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/qubo_smoke.json --out /tmp/apc-qubo-sweep-0-4.json
PYTHONPATH=src python3 scripts/run_benchmark_sweep.py benchmarks/sweeps/maxsat_smoke.json --out /tmp/apc-maxsat-sweep-0-4.json
python3 scripts/collect_release_artifacts.py --tag v0.4.0-alpha.N --verify /tmp/apc-release-verify-full-0-4.json --out /tmp/apc-release-artifacts-0-4.json
PYTHONPATH=src python3 scripts/inspect_runtime_debug.py examples/specs/qubo_tiny.json --release-artifacts /tmp/apc-release-artifacts-0-4.json --out /tmp/apc-runtime-debug-0-4.json
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts-0-4.json --out /tmp/apc-release-artifacts-summary-0-4.json
```

## Required Evidence

```text
QUBO CUDA move scoring parity
CUDA parity report
runtime CLI family routing
run artifact writer
native host bridge request/result records
benchmark timing fields with operator names
contributor operator extension guide
runtime debug report
0.4 beta debug checkpoint
release artifact collection
public terminology boundary scan
```

## Required Public Schemas

```text
apc.cuda_parity_report.v1
apc.run_artifacts.v1
apc.runtime_debug_report.v1
apc.runtime_debug_beta_checkpoint.v1
apc.native_host_bridge.v1
apc.benchmark_sweep.v1
apc.release_artifacts.v1
```

## Limits

```text
No drop-in solver replacement claim.
No solver compatibility promise before a checked adapter exists.
No performance claim without complete timing evidence.
CUDA unavailable status is acceptable only when recorded explicitly.
```
