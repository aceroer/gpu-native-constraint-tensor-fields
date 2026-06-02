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

Then inspect the collected evidence:

```bash
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts.json
```

Or run the evidence route as one smoke command:

```bash
python3 scripts/smoke_release_evidence.py --tag v0.1.0-alpha.N --out /tmp/apc-release-evidence-smoke.json
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
maintenance release procedure
runtime execution contract
operator call ledger tests
runtime status code tests
native host ABI header tests
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
apc.release_artifacts_summary.v1
apc.release_evidence_smoke.v1
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

Maintenance tags should also keep:

```text
docs/MAINTENANCE_RELEASES.md
docs/RUNTIME_CONTRACT.md
tests/test_maintenance_releases.py
tests/test_runtime_contract.py
tests/test_operator_call_ledger.py
tests/test_runtime_status.py
tests/test_native_host_abi.py
```

## Reader

The reader emits a compact factual summary:

```text
schema: apc.release_artifacts_summary.v1
source_schema
source_path
status
tag
commit
artifact_count
artifact_schemas
fixture_count
check_count
failed_checks
notes
```

The reader reports the evidence that is present in the collected artifact. It
does not infer release quality or compatibility beyond the recorded checks.

## Smoke Command

The smoke command runs:

```text
scripts/verify_public_release.py
scripts/collect_release_artifacts.py
scripts/inspect_release_artifacts.py
```

It emits:

```text
schema: apc.release_evidence_smoke.v1
status
tag
mode
paths
steps
notes
```

The smoke report records output paths and step return codes. If any step fails,
later evidence steps are skipped and the report status is `failed`.

## Maintenance Tags

Maintenance release procedures are recorded in:

```text
docs/MAINTENANCE_RELEASES.md
```

The procedure uses the smoke command as the compact evidence route for 0.1.x
patch tags.
