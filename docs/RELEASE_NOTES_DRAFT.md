# Release Notes Draft

## Scope

This draft summarizes the current public state of the GPU-native constraint
runtime prototype.

## Highlights

```text
Native binary MILP problem specs.
CTIR lowering and inspection.
CPU reference repair runtime.
Device layout planning and layout materialization.
Operator registry with CPU references and CUDA ABI names.
CUDA skeleton and unavailable-path benchmark handling.
Benchmark harness with explicit timing fields.
MaxSAT reading path and CPU repair example.
StatePool, BranchTensor, ReductionGate, and InterfaceProjection layers.
Vector-native repair demo and projected demo benchmark report.
Public quickstart and handoff docs.
Release verifier and release checklist for tag readiness.
Release artifact contract for repeatable tag evidence.
```

## Stable Commands

```bash
PYTHONPATH=src python3 -m apc.cli validate examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli run examples/specs/binary_milp_tiny.json --max-iters 2 --ledger-out /tmp/apc-ledger.json
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-bench.json --max-iters 2
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo-bench.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.N --out /tmp/apc-release-artifacts.json
```

## Release Readiness

```text
The release verifier emits schema apc.public_release_verification.v1.
The release checklist names tag, docs, tests, and benchmark artifacts.
The release artifact contract emits schema apc.release_artifacts.v1.
Full verification is available through scripts/verify_public_release.py --full.
```

## Current Limits

```text
No full MIP optimality proof.
No drop-in replacement for existing solvers.
CUDA kernels are still narrow and guarded by CPU differential tests.
Compatibility adapters are intentionally narrow.
```

## Next Work

```text
Public benchmark sweeps.
Additional problem-family demos.
More CUDA operator coverage.
Small release tag after another clean verification pass.
First public tag preparation.
```
