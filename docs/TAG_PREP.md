# Tag Preparation

This document prepares the first public tag candidate.

## Candidate

```text
candidate_tag: v0.1.0-alpha.0
verified_commit: fill from /tmp/apc-release-artifacts.json commit
release_artifact_schema: apc.release_artifacts.v1
release_verifier_schema: apc.public_release_verification.v1
```

Use the candidate tag only after the verifier and artifact collector both
report `status: ok`.

## Commands

Run from the repository root:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
```

The quick verifier run writes the benchmark artifacts consumed by the collector.

## Required Artifacts

Keep these files for the tag candidate:

```text
/tmp/apc-release-verify-full.json
/tmp/apc-release-verify.json
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-release-artifacts.json
```

Required release artifact checks:

```text
verifier_schema: ok
verifier_status: ok
cpu_benchmark_schema: ok
vector_demo_benchmark_schema: ok
docs_present: ok
tests_present: ok
```

## Release Notes Fields

Before creating the tag, release notes should expose these fields:

```text
candidate_tag
verified_commit
release_verifier_artifact
release_artifact_report
cpu_benchmark_artifact
vector_demo_benchmark_artifact
```

## Limits

The first public tag is still an early prototype. Keep these limits visible:

```text
No full MIP optimality proof.
No drop-in replacement for existing solvers.
CUDA kernels are still narrow and guarded by CPU differential tests.
Compatibility adapters are intentionally narrow.
No broad performance claim without CUDA timing evidence.
```

## Non-Goals

Do not use this tag to claim:

```text
Full solver compatibility.
Production CUDA coverage.
Guaranteed optimality.
GPU speedup without measured copy-time accounting.
Stable external adapter compatibility.
```

## Tag Step

After all evidence is clean, the tag command should use the verified commit:

```bash
git tag -a v0.1.0-alpha.0 <verified_commit> -m "v0.1.0-alpha.0"
git push origin v0.1.0-alpha.0
```

Do not create the tag if the working tree is dirty or if the artifact report
commit differs from the intended tag commit.
