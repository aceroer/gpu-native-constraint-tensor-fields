# Cross-Project Handoff

This document sketches a public handoff between this GPU-native constraint
runtime release and the paired vector-native runtime project.

## Releases

```text
gpu_project: gpu-native-constraint-tensor-fields
gpu_tag: v0.1.0-alpha.0
gpu_tag_commit: b051c20b38ff19cf99992daa72dc1e9558ec7b84
gpu_release_artifact_schema: apc.release_artifacts.v1

paired_project: vAgentRT
paired_tag: v0.1.0
paired_tag_commit: 69c14675c14fbad0c72f6bb719ac362872446ae7
```

This is a handoff sketch, not a compatibility claim.

## Stable GPU Entry Points

The GPU-native constraint runtime side exposes:

```text
problem specs
CTIR lowering
StatePool
BranchTensor
ReductionGate
InterfaceProjection
release verifier
release artifact collector
benchmark artifacts
```

Stable public files:

```text
README.md
ROADMAP.md
docs/QUICKSTART.md
docs/PUBLIC_HANDOFF.md
docs/RELEASE_ARCHIVE.md
docs/RELEASE_ARTIFACTS.md
scripts/verify_public_release.py
scripts/collect_release_artifacts.py
```

## Stable Paired Runtime Entry Points

The paired vector-native runtime side exposes:

```text
state pool
branch generator
vector scorer
semantic emission gate
action reducer
execution ledger
benchmark harness
task packs
```

Stable public files in the paired project include:

```text
README.md
docs/QUICKSTART.md
docs/API_REFERENCE.md
docs/APC_ADAPTER.md
docs/BACKENDS.md
docs/BENCHMARKING.md
docs/INTEGRATION_NOTES.md
docs/TASK_PACKS.md
CHANGELOG.md
```

## Handoff Shape

The public connection is:

```text
paired runtime task state
-> action candidate set
-> GPU-compatible state pool sketch
-> branch tensor / scoring sketch
-> reduction output
-> interface projection
-> paired runtime action or report
```

For now, this route is a sketch for future adapter work. It should preserve the
native entry points on both sides.

## Evidence Contract

The GPU side uses:

```text
apc.public_release_verification.v1
apc.benchmark.v1
apc.vector_demo_benchmark.v1
apc.release_artifacts.v1
```

The handoff should start by carrying:

```text
gpu_tag
gpu_tag_commit
gpu_release_artifact_schema
paired_tag
paired_tag_commit
run_id
state_pool_size
branch_count
selected_action_count
projection_kind
benchmark_notes
```

## Non-Compatibility Statement

This release does not claim:

```text
drop-in solver compatibility
drop-in paired runtime compatibility
production CUDA coverage
guaranteed optimality
GPU speedup without measured copy-time accounting
stable external adapter ABI
```

## Next Work

The next public step should be a small adapter sketch that maps one paired
runtime task pack into the GPU-side StatePool, BranchTensor, ReductionGate, and
InterfaceProjection path while keeping both release artifacts reproducible.
