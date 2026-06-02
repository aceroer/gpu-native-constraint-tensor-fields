# Release Checklist

Use this checklist before creating a public tag.

## Tag

```text
Choose a tag name.
Confirm the tag points to main after release verification passes.
Record the commit hash in the release notes.
```

Suggested early tag shape:

```text
v0.1.0-alpha.N
```

## Verification

Run the public release verifier:

```bash
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
```

For a tag candidate, also run full mode:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
```

Required verifier evidence:

```text
status is ok
mode is quick or full as intended
compileall passed
quickstart tests passed
public docs tests passed
CPU benchmark smoke passed
vector-native demo benchmark smoke passed
public terminology boundary scan passed
```

## Docs

Review these public docs before tagging:

```text
README.md
ROADMAP.md
docs/QUICKSTART.md
docs/PUBLIC_HANDOFF.md
docs/VERIFY_RELEASE.md
docs/RELEASE_NOTES_DRAFT.md
docs/RELEASE_ARTIFACTS.md
docs/TAG_PREP.md
LICENSE
NOTICE
CITATION.cff
docs/ORIGIN.md
```

Required doc evidence:

```text
Quickstart commands are still runnable.
Roadmap names the current completed phase and next phase.
Release notes summarize the public feature surface.
Handoff doc names stable entry points and extension areas.
LICENSE contains the MIT License text.
NOTICE names the original repository and recommended attribution.
CITATION.cff names the repository and author.
Origin doc records the first public source line.
Release artifact doc names verifier, benchmark, tests, docs, and commit evidence.
Tag prep names the candidate tag, verified commit field, and stop conditions.
No private-only terminology appears in public docs.
```

## Tests

The minimum public test evidence is:

```bash
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
```

CUDA-specific tests may skip when `nvcc` is unavailable. A skip is acceptable only
when the skip reason clearly states that CUDA tooling is unavailable.

## Benchmark Artifacts

Keep these benchmark artifact paths for a tag candidate:

```text
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-release-verify.json
/tmp/apc-release-verify-full.json
/tmp/apc-release-artifacts.json
```

Required benchmark evidence:

```text
CPU benchmark emits schema apc.benchmark.v1.
Vector-native demo benchmark emits payload.benchmark.schema apc.vector_demo_benchmark.v1.
Verifier report emits schema apc.public_release_verification.v1.
Release artifact report emits schema apc.release_artifacts.v1.
Benchmark notes do not claim GPU speedup without CUDA timing evidence.
```

## Release Notes

Before publishing a tag:

```text
Update docs/RELEASE_NOTES_DRAFT.md with the tag name.
Record the verified commit hash.
List the verifier output path.
List the benchmark artifact paths.
List the release artifact output path.
Keep current limits visible.
```

## Stop Conditions

Do not create a public tag if any item is true:

```text
The release verifier fails.
The public terminology boundary scan reports a match.
Quickstart commands no longer run from the repository root.
Benchmark artifacts are missing or have unexpected schemas.
Release notes are stale relative to ROADMAP.md.
```
