# 0.2 Tag Execution

This document records the procedure for a future public `0.2` tag.

It is a procedure, not a claim that the tag already exists.

## Candidate

```text
candidate_tag: v0.2.0-alpha.N
candidate_commit: fill from git rev-parse HEAD
artifact_commit: fill from /tmp/apc-release-artifacts-0-2.json commit
tag_kind: pending
```

The candidate commit must match the artifact report commit before a tag is
created.

## Required Evidence

Run full verification:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
```

Collect artifacts:

```bash
python3 scripts/collect_release_artifacts.py --tag v0.2.0-alpha.N --out /tmp/apc-release-artifacts-0-2.json
```

Inspect artifacts:

```bash
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts-0-2.json --out /tmp/apc-release-artifacts-summary-0-2.json
```

Run evidence smoke:

```bash
python3 scripts/smoke_release_evidence.py --tag v0.2.0-alpha.N --out /tmp/apc-release-evidence-smoke-0-2.json
```

## Commit Match Check

Before creating the tag, verify:

```bash
git rev-parse HEAD
python3 - <<'PY'
import json
from pathlib import Path
print(json.loads(Path("/tmp/apc-release-artifacts-0-2.json").read_text())["commit"])
PY
```

The two commit hashes must match.

## Tag Creation

Only after every required evidence command reports `ok`:

```bash
git tag -a v0.2.0-alpha.N -m "v0.2.0-alpha.N"
git rev-parse v0.2.0-alpha.N^{commit}
git rev-parse HEAD
```

The tag commit and `HEAD` must match before pushing.

## Remote Verification

After pushing the tag, verify:

```bash
git ls-remote --tags origin 'v0.2.0-alpha.N*'
```

The peeled tag commit must match the artifact report commit.

## Archive Finalization

After remote tag verification succeeds, update:

```text
docs/RELEASE_ARCHIVE_0_2.md
```

Replace candidate fields with final fields:

```text
candidate_tag -> tag
candidate_commit -> tag_commit
tag_kind: pending -> tag_kind: annotated
```

Keep the evidence paths and schema records in the archive.

## Stop Conditions

Do not create or push the tag if any item is true:

```text
Full verifier status is not ok.
Release artifact status is not ok.
Release artifact summary status is not ok.
Release evidence smoke status is not ok.
Candidate commit does not match artifact report commit.
Problem-family fixture index status is not ok.
Benchmark sweep summary status is not ok.
Public terminology boundary scan is not empty.
```

## Limits

The public `0.2` tag remains bounded:

```text
No full MIP, MaxSAT, or QUBO optimality proof.
No drop-in replacement for existing solvers.
QUBO execution remains planned.
No accelerator comparison claim is made without complete timing evidence.
```
