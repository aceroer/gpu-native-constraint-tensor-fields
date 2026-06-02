# Phase 38 Completion

Phase 38 added a one-command smoke route for public release evidence.

## Added

```text
scripts/smoke_release_evidence.py
tests/test_release_evidence_smoke.py
```

## Smoke Contract

The smoke command runs these steps in order:

```text
verifier
collector
reader
```

It emits:

```text
apc.release_evidence_smoke.v1
```

The smoke report records:

```text
verifier output path
collector output path
reader output path
step commands
step return codes
step output existence
```

If one step fails, later steps are skipped and the smoke report status is
`failed`.

## Verification

Observed checks:

```text
tests/test_release_evidence_smoke.py: OK
tests/test_release_artifact_reader.py: OK
tests/test_release_artifacts.py: OK
release evidence smoke command: ok
public boundary scan: empty
```

## Next Step

Phase 39 should add a 0.1.x maintenance tag procedure that uses the smoke
command as the compact evidence route.
