# Origin

This document records the public source lineage for GPU-Native Constraint
Tensor Fields.

## Project

```text
Name: GPU-Native Constraint Tensor Fields
Original author: aceroer
Original repository: https://github.com/aceroer/gpu-native-constraint-tensor-fields
First public source date: 2026-06-02
License: MIT
```

## Core Public Claim

This project explores constraint solving as GPU-native state evolution rather
than as a direct port of scalar search-tree execution.

The public runtime path is:

```text
problem spec
-> CTIR lowering
-> device layout planning
-> operator registry
-> state pool
-> branch tensor
-> reduction gate
-> interface projection
-> validation and benchmark ledger
```

## First Public Surface

The first public source line includes:

```text
CPU reference repair runtime
CUDA ABI and kernel skeleton
CTIR lowering
device layout planning
operator registry
StatePool
BranchTensor
ReductionGate
InterfaceProjection
vector-native repair demo
release verifier
release checklist
```

## Citation

Recommended citation:

```text
aceroer. GPU-Native Constraint Tensor Fields. 2026.
https://github.com/aceroer/gpu-native-constraint-tensor-fields
```

Structured citation metadata is in:

```text
CITATION.cff
```

## Source Lineage

The repository history, completion records, release notes, and release verifier
are the public evidence trail for this project.

Important public source documents:

```text
README.md
ROADMAP.md
docs/RELEASE_NOTES_DRAFT.md
docs/PUBLIC_HANDOFF.md
docs/VERIFY_RELEASE.md
docs/RELEASE_CHECKLIST.md
LICENSE
NOTICE
CITATION.cff
```

Derivative work should preserve the license text and should cite the original
repository when used in research, public benchmarks, technical reports, or
derivative libraries.
