# Tag Execution

This document records the first public tag execution.

## Final Tag

```text
final_tag: v0.1.0-alpha.0
tag_target: current release evidence commit
release_artifact_schema: apc.release_artifacts.v1
release_verifier_schema: apc.public_release_verification.v1
```

The tag must point to the same commit reported by:

```bash
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
```

## Evidence Artifacts

The tag execution keeps these artifact paths:

```text
/tmp/apc-release-verify-full.json
/tmp/apc-release-verify.json
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-release-artifacts.json
```

Required clean evidence:

```text
release verifier status: ok
release artifact status: ok
public terminology boundary scan: empty
unittest suite: OK, with CUDA tests allowed to skip only when nvcc is unavailable
```

## Tag Verification

Verify the local tag:

```bash
git rev-parse v0.1.0-alpha.0^{commit}
git rev-parse HEAD
```

The two commit hashes must match before pushing the tag.

Verify the remote tag after pushing:

```bash
git ls-remote --tags origin v0.1.0-alpha.0
```

## Release Notes Fields

Release notes record:

```text
final_tag
tag_target
release_verifier_artifact
release_verifier_full_artifact
release_artifact_report
cpu_benchmark_artifact
vector_demo_benchmark_artifact
```

## Public Boundary

The tag preserves the public language boundary:

```text
No private-only terminology appears in public docs.
No private notes are included in the repository.
No broad GPU speedup claim appears without CUDA copy-time accounting.
```

## Limits

The first public tag remains an alpha prototype:

```text
No full MIP optimality proof.
No drop-in replacement for existing solvers.
CUDA kernels are still narrow and guarded by CPU differential tests.
Compatibility adapters are intentionally narrow.
```
