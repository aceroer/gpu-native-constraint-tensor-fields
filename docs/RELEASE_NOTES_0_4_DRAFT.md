# 0.4 Release Notes Draft

Candidate tag:

```text
v0.4.0-alpha.N
```

## Highlights

```text
QUBO CUDA move scoring parity target
CUDA parity report inspector
family-routed runtime CLI for binary_milp, qubo, and maxsat
stable run artifact directories
native host bridge request/result records
benchmark sweep operator fields
contributor operator extension guide
runtime debug report
0.4 beta debug checkpoint for compute mode, host role, compiler readiness, release artifact status, and PCI/HAL boundary status
```

## Evidence

0.4 evidence should include:

```text
/tmp/apc-release-verify-full-0-4.json
/tmp/apc-cuda-parity-report-0-4.json
/tmp/apc-runtime-debug-0-4.json
/tmp/apc-binary-milp-sweep-0-4.json
/tmp/apc-qubo-sweep-0-4.json
/tmp/apc-maxsat-sweep-0-4.json
/tmp/apc-release-artifacts-0-4.json
/tmp/apc-release-artifacts-summary-0-4.json
```

## Limits

This release candidate is still a compact native-runtime research build. It
does not claim solver API compatibility, full optimization coverage, or
performance advantage. CUDA unavailable cases remain factual environment
statuses.
