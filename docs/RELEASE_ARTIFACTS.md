# Release Artifacts

Release artifact normalization collects tag evidence into one JSON-ready report.

## Collector

Run the release verifier first:

```bash
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
```

Then collect release evidence:

```bash
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.N --out /tmp/apc-release-artifacts.json
```

The collector reads:

```text
/tmp/apc-release-verify.json
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-handoff-fixtures.json
```

The verifier creates the benchmark artifacts during quick and full runs.

## Schema

The collector emits:

```text
schema: apc.release_artifacts.v1
status
tag
commit
artifacts
docs
tests
examples
checks
```

## Required Evidence

The artifact contract records:

```text
release verifier schema and status
CPU benchmark schema
vector-native demo benchmark schema
handoff fixture listing schema and status
release docs
release tests
checked handoff fixture examples
current commit hash
```

Required schemas:

```text
apc.public_release_verification.v1
apc.benchmark.v1
apc.vector_demo_benchmark.v1
apc.handoff_fixture_index.v1
vagent.apc_handoff_report.v1
apc.cross_project_handoff_check.v1
apc.checked_handoff_runtime_demo.v1
apc.release_artifacts.v1
```

## Release Use

For a tag candidate, keep:

```text
/tmp/apc-release-verify.json
/tmp/apc-release-verify-full.json
/tmp/apc-release-bench.json
/tmp/apc-release-vector-demo-bench.json
/tmp/apc-handoff-fixtures.json
/tmp/apc-release-artifacts.json
```

The release notes should reference this artifact contract when a public tag is
prepared.
