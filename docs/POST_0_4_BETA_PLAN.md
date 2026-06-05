# Post-0.4 Beta Plan

This document defines the public 0.4 beta route after the remote Windows CUDA
test pass. The main lesson is that the CUDA operator lane is cleaner than the
Windows toolchain lane. 0.4 beta should keep those responsibilities separate.

## Stage Name

```text
0.4 Beta Real-Environment Split
```

## Stage Goal

Move from a candidate release that can run on a developer machine to a beta
release that has a clear real-environment split:

```text
TCC or headless CUDA compute core
-> stable runtime evidence
-> Windows orchestration layer
-> logs, artifacts, and result handoff
```

The beta target is not to make Windows the primary compiler or release authority.
Windows can host the GPU, schedule runs, collect logs, and return artifacts, but
the lower compute lane should remain a small, reproducible CUDA runtime path.

The longer architecture target is lower than TCC:

```text
PCI hardware contract
-> GPU HAL
-> CUDAOS-owned device control
-> cross-OS orchestration
```

In that model, PCI/PCIe enumeration is the only CPU-side hardware contract. The
HAL is the cross-system glue layer that hides WDDM, TCC, and Linux kernel-device
differences. The GPU runtime owns device control above that layer, including
register-level and PCI BAR-space evidence where public tooling can expose it.
This is a target architecture, not a claim that the current beta bypasses vendor
drivers or OS security boundaries.

The open-source line should stay at the reproducible CUDA/HAL boundary: checked
operators, public evidence reports, and hardware facts that contributors can
inspect without privileged device takeover. The reason is not purely commercial:
deeper GPU ownership can challenge vendor driver, security, support, and
ecosystem boundaries. If a later customer needs stronger BAR, register,
scheduling, or device-lifetime control, the appropriate sequence is vendor and
customer agreement first, then a restricted closed-source hardware-control layer
after the interface, permission, and responsibility boundaries are clear. That
layer is an agreed implementation path for sensitive control surfaces, not the
main reason for the project to exist. Its work should start only after the
customer and GPU vendor settle the operating boundary and bring the development
request back with explicit permissions. It may share the public artifact formats
and debug vocabulary, but it should not be required for the public runtime to
remain useful.

## Remote Test Lesson

The remote test exposed four different failure classes:

```text
CUDA operator failures
CUDA environment failures
host compiler and build-tool failures
shell, path, and packaging failures
```

The CUDA operator failures did not appear in the final evidence pass. The real
problems were orchestration-level issues: SSH user selection, MSVC environment
initialization, POSIX-style command examples on Windows, missing CMake in the
remote PATH, and macOS metadata files in a Windows test snapshot.

0.4 beta should preserve that distinction. A failed Windows command must not be
misread as a failed CUDA operator. A working CUDA operator must not imply that
the Windows host is a reliable release environment.

## Architecture Rule

Use this rule for 0.4 beta and later real-environment work:

```text
core runtime first
Windows orchestration second
```

The compute core should prefer:

```text
PCI/PCIe hardware identity as the lowest public contract
TCC mode where available
headless CUDA execution where TCC is unavailable
explicit nvcc, device, arch, and driver facts
small differential tests against CPU references
release evidence that can be reproduced without UI state
```

The Windows layer should provide:

```text
SSH or local task launch
MSVC or CUDA environment initialization
artifact directory setup
log collection
JSON evidence handoff
structured status for missing tools
```

The Windows layer should avoid:

```text
owning CUDA operator semantics
being the only release-verification path
hiding shell or path failures as CUDA failures
claiming performance from orchestration timing alone
```

## Workstream A: TCC/Headless Compute Lane

Purpose: make the lower CUDA lane stable enough that tests can tell the
difference between operator behavior and host orchestration.

Deliverable shape:

```text
scripts/inspect_cuda_parity.py
scripts/inspect_runtime_debug.py
docs/DEBUGGING.md
tests/cuda/
```

Acceptance:

```text
Debug reports record driver, device, nvcc, selected arch, and execution mode.
CUDA differential tests remain paired with CPU references.
The report can state whether the target is TCC, WDDM, or headless CUDA.
Missing TCC is recorded as an environment fact, not a failure by itself.
```

## Workstream A2: PCI/HAL Contract Sketch

Purpose: define the eventual hardware-level contract below TCC, WDDM, and Linux
device models without overclaiming current control of the GPU.

Deliverable shape:

```text
docs/POST_0_4_BETA_PLAN.md
docs/DEBUGGING.md
future HAL inspection reports
```

Acceptance:

```text
PCI/PCIe enumeration is named as the CPU-side hardware discovery boundary.
The HAL is named as the layer that normalizes WDDM, TCC, and Linux device differences.
CUDAOS ownership is described as a target for GPU-side control above the HAL.
Register and PCI BAR-space inspection are treated as evidence surfaces, not public stability promises.
Deeper hardware takeover waits for vendor/customer agreement before restricted closed-source development.
```

## Workstream B: Windows Orchestration Layer

Purpose: make Windows useful as a remote GPU host without letting it define the
core runtime.

Deliverable shape:

```text
scripts/
docs/DEBUGGING.md
docs/RELEASE_CHECKLIST_0_4.md
```

Acceptance:

```text
Windows runs can initialize MSVC/CUDA tools before nvcc tests.
Windows evidence commands use platform-correct path and environment handling.
Remote logs are collected as artifacts.
Shell, path, and packaging failures are classified separately from CUDA failures.
```

## Workstream C: Beta Evidence Package

Purpose: make 0.4 beta evidence useful to a contributor who has either a Linux
CUDA machine or a Windows GPU host.

Deliverable shape:

```text
docs/RELEASE_NOTES_0_4_DRAFT.md
docs/RELEASE_ARCHIVE_0_4.md
docs/RELEASE_ARTIFACTS.md
```

Acceptance:

```text
Evidence names local, remote, CUDA, and orchestration status.
CUDA available status is separated from host-toolchain readiness.
Skipped native/CMake checks name the missing tool.
No performance claim is made from remote timing alone.
```

## Beta Stop Conditions

Do not call 0.4 beta ready if any item is true:

```text
CUDA operator failures and Windows orchestration failures are mixed together.
Debug reports cannot explain why nvcc, device, arch, or host compiler is missing.
Remote evidence cannot be reproduced from a clean checkout or snapshot.
Windows path or shell assumptions break the public smoke route.
Release artifacts omit the QUBO CPU reference evidence.
Public docs imply Windows is the primary compute-core authority.
Public docs claim direct PCI BAR or register control before a checked HAL exists.
Public docs frame deeper hardware takeover as a public default instead of a vendor-agreed restricted path.
```

## Next Concrete Step

The beta debug/evidence checkpoint is now part of `apc.runtime_debug_report.v1`.
It records:

```text
compute mode: TCC, WDDM, or headless CUDA
host role: compute core or orchestration layer
host compiler readiness
CUDA differential-test status
release artifact status
PCI/HAL boundary status
```

The next concrete step is to generate and inspect the 0.4 beta evidence package
with that checkpoint included.
