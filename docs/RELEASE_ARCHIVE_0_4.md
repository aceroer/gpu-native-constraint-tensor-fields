# 0.4 Release Archive

This archive is a candidate archive until a 0.4 tag is created and verified.

## Candidate Tag

```text
v0.4.0-alpha.N
```

## Required Evidence Paths

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

## Evidence Surface

```text
0.4 route plan
QUBO CUDA move scoring parity
CUDA parity report
runtime CLI family routing
run artifact writer
native host bridge consolidation
benchmark timing expansion
contributor extension guide
runtime debug tools
0.4 beta debug checkpoint
release checklist
tag execution procedure
```

## Finalization Rule

This archive becomes final only after:

```text
the candidate tag exists
the tag commit matches release artifact commit
full verification passes
release artifact inspection passes
public boundary scan passes
```
