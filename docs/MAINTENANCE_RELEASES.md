# Maintenance Releases

This document defines the compact procedure for 0.1.x maintenance tags.

Maintenance tags are for public evidence updates, small fixes, and documentation
repairs after the first alpha tag. They should not introduce broad compatibility
claims or new performance claims.

## Patch Tag Shape

Use this tag shape:

```text
v0.1.x
v0.1.x-alpha.N
```

Required inputs:

```text
candidate_patch_tag
intended_commit
base_tag
release_evidence_smoke_report
release_artifact_report
release_artifact_summary
```

The intended commit must be the same commit reported by the release artifact
summary.

## Evidence Command

Run the compact evidence route from the repository root:

```bash
python3 scripts/smoke_release_evidence.py --tag <candidate_patch_tag> --out /tmp/apc-release-evidence-smoke.json
```

For a fuller local check before tagging, run:

```bash
python3 scripts/smoke_release_evidence.py --full --tag <candidate_patch_tag> --out /tmp/apc-release-evidence-smoke.json
```

The smoke command produces:

```text
/tmp/apc-release-verify.json
/tmp/apc-release-artifacts.json
/tmp/apc-release-artifacts-summary.json
/tmp/apc-release-evidence-smoke.json
```

With `--full`, the verifier output path is:

```text
/tmp/apc-release-verify-full.json
```

## Required Evidence

Before creating a maintenance tag, confirm:

```text
release evidence smoke status: ok
release artifact status: ok
release artifact summary status: ok
release artifact summary commit: intended_commit
release artifact summary tag: candidate_patch_tag
failed checks: []
public boundary scan: empty
working tree: clean
```

Required schemas:

```text
apc.release_evidence_smoke.v1
apc.public_release_verification.v1
apc.release_artifacts.v1
apc.release_artifacts_summary.v1
```

## Tag Command

Create the annotated tag only after the evidence is clean:

```bash
git tag -a <candidate_patch_tag> <intended_commit> -m "<candidate_patch_tag>"
git push origin <candidate_patch_tag>
```

Verify the remote tag:

```bash
git ls-remote --tags origin '<candidate_patch_tag>*'
```

The peeled remote tag commit should match `intended_commit`.

## Archive Fields

Record these fields in release notes or an archive note:

```text
patch_tag
base_tag
tag_target
release_evidence_smoke_report
release_artifact_report
release_artifact_summary
release_verifier_artifact
failed_checks
limits
```

## Refusal Conditions

Do not create a maintenance tag when:

```text
the working tree is dirty
the smoke report status is failed
the artifact report status is failed
the summary commit differs from intended_commit
the summary tag differs from candidate_patch_tag
failed_checks is not empty
public boundary scan is not empty
the change requires a new minor release instead of a patch tag
```

## Scope Limits

Maintenance tags may include:

```text
documentation repairs
release evidence procedure repairs
small test corrections
small public fixture repairs
minor script fixes that do not change public runtime contracts
```

Maintenance tags should not include:

```text
new runtime contracts
new CUDA operator coverage
new adapter promises
new benchmark claims
new solver compatibility claims
```

## Public Wording

Keep the release note factual:

```text
This maintenance tag updates public release evidence and small repository
checks. It does not change the project limits or add compatibility claims.
```
