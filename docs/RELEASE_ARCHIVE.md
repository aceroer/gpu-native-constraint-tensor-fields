# Release Archive

This document is the durable handoff for the first public release tag.

## Archived Tag

```text
tag: v0.1.0-alpha.0
tag_commit: b051c20b38ff19cf99992daa72dc1e9558ec7b84
tag_kind: annotated
release_artifact_schema: apc.release_artifacts.v1
release_verifier_schema: apc.public_release_verification.v1
```

Remote tag verification:

```bash
git ls-remote --tags origin 'v0.1.0-alpha.0*'
```

Expected peeled tag commit:

```text
b051c20b38ff19cf99992daa72dc1e9558ec7b84 refs/tags/v0.1.0-alpha.0^{}
```

## Evidence Artifacts

Keep or regenerate these evidence files:

```text
/tmp/apc-release-verify-full.json
/tmp/apc-release-verify.json
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-release-artifacts.json
```

Evidence schemas:

```text
/tmp/apc-release-verify.json -> apc.public_release_verification.v1
/tmp/apc-release-bench.json -> apc.benchmark.v1
/tmp/apc-release-vector-demo-bench.json -> apc.vector_demo_benchmark.v1
/tmp/apc-release-artifacts.json -> apc.release_artifacts.v1
```

## Reproduce Evidence

From the repository root:

```bash
git fetch --tags origin
git checkout v0.1.0-alpha.0
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
```

The quick verifier run creates:

```text
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
```

Expected archive evidence:

```text
release verifier status: ok
release artifact status: ok
artifact report commit: b051c20b38ff19cf99992daa72dc1e9558ec7b84
public terminology boundary scan: empty
unittest suite: OK, with CUDA tests allowed to skip only when nvcc is unavailable
```

## Benchmark Evidence

CPU benchmark evidence:

```text
schema: apc.benchmark.v1
path: /tmp/apc-release-bench.json
speedup claim: none
copy-time accounting: explicit
```

Vector-native demo benchmark evidence:

```text
schema: apc.vector_demo_benchmark.v1
path: /tmp/apc-release-vector-demo-bench.json
runtime path: CTIR -> StatePool -> BranchTensor -> ReductionGate -> InterfaceProjection
speedup claim: none
copy-time accounting: explicit
```

## Handoff Notes

This release is an alpha handoff for public inspection and extension.

Keep current limits visible:

```text
No full MIP optimality proof.
No drop-in replacement for existing solvers.
CUDA kernels are still narrow and guarded by CPU differential tests.
Compatibility adapters are intentionally narrow.
No broad GPU speedup claim without CUDA timing evidence.
```

The next public work should extend release archiving and then move toward the
cross-project handoff when the paired runtime project is ready to merge routes.
