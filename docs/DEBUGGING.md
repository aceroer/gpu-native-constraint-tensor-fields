# Debugging

Runtime debug reports are public inspection evidence for real-environment
failures.

Generate a report with:

```bash
PYTHONPATH=src python3 scripts/inspect_runtime_debug.py examples/specs/qubo_tiny.json --out /tmp/apc-runtime-debug.json
```

With run artifacts:

```bash
PYTHONPATH=src python3 -m apc.cli run examples/specs/qubo_tiny.json --family auto --artifact-dir /tmp/apc-runs --run-id qubo_debug
PYTHONPATH=src python3 scripts/inspect_runtime_debug.py examples/specs/qubo_tiny.json --artifact-dir /tmp/apc-runs/qubo_debug --out /tmp/apc-runtime-debug.json
```

The report emits:

```text
schema: apc.runtime_debug_report.v1
spec
lowered CTIR
layout summary
ledger summary
run artifacts
runtime status codes
CUDA debug facts
```

CUDA debug fields include:

```text
nvcc_available
device_available
driver_version
driver_model
selected_arch
skip_reason
```

0.4 beta debug checkpoints also include:

```text
beta_checkpoint.schema: apc.runtime_debug_beta_checkpoint.v1
compute_mode: tcc, wddm, headless_cuda_or_driver_default, or cuda_unavailable
host_role: compute_core or orchestration_layer
host_compiler_readiness
cuda_differential_test_status
release_artifact_status
pci_hal_boundary_status
```

Debug reports should avoid local absolute paths in public fields. Use spec
names, run ids, artifact-relative file names, and structured status values.

Every version after 0.4 should keep a debug-tooling checkpoint before release
evidence is closed.

## Real-Environment Split

Remote GPU tests should classify failures before interpreting them. The main
classes are:

```text
CUDA operator failures
CUDA environment failures
host compiler and build-tool failures
shell, path, and packaging failures
```

The compute core should prefer a TCC or headless CUDA lane where available. When
that is not available, the report should state the actual mode and keep the
evidence factual. Missing TCC is an environment fact; it is not the same as an
operator failure.

Windows hosts should be treated as orchestration layers unless a later checked
adapter says otherwise. A Windows orchestration layer may launch tasks,
initialize MSVC or CUDA environment scripts, prepare artifact directories,
collect logs, and return JSON evidence. It should not own CUDA operator
semantics or hide shell, path, CMake, MSVC, or packaging failures as CUDA
failures.

For 0.4 beta, the public architecture rule is:

```text
core runtime first
Windows orchestration second
```

The longer hardware target is:

```text
PCI hardware contract
-> GPU HAL
-> CUDAOS-owned device control
-> cross-OS orchestration
```

In that target, the CPU-side OS only provides PCI/PCIe enumeration and process
orchestration. A GPU HAL normalizes WDDM, TCC, and Linux kernel-device
differences, while the GPU runtime owns the device-control lane above it.
Register-level and PCI BAR-space facts should be reported as hardware evidence
surfaces when tooling can inspect them. They should not be presented as stable
public API promises before a checked HAL exists.

The public runtime should remain useful without privileged GPU takeover. If a
future branch needs stronger BAR, register, scheduling, or device-lifetime
control, treat that as a vendor-agreed restricted hardware-control layer rather
than a public default. The customer, GPU vendor, interface permissions, and
support responsibilities should be settled before development starts, and the
implementation request should come back with explicit permission to touch those
sensitive control surfaces. Public debug reports can still define the evidence
vocabulary for that layer, but the open-source route should not depend on restricted control to pass its checks.
