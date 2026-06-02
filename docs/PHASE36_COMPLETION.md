# Phase 36 Completion

Phase 36 attaches the handoff fixture listing helper to release evidence.

## Added

```text
scripts/verify_public_release.py handoff_fixture_listing_artifact check
scripts/collect_release_artifacts.py handoff_fixture_listing artifact
docs/RELEASE_ARTIFACTS.md fixture listing artifact schema
tests/test_release_artifacts.py fixture listing evidence checks
```

## Acceptance

```text
Release artifacts include apc.handoff_fixture_index.v1 evidence.
Collector checks the fixture index schema and status.
Release notes keep fixture listing scoped to public inspection evidence.
```

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest tests.test_release_artifacts -v
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
```

Observed result:

```text
tests/test_release_artifacts.py: OK
release verifier status: ok
artifact collector status: ok
handoff_fixture_listing_schema: ok
handoff_fixture_listing_status: ok
```

The next phase should add a compact release evidence reader so users can inspect
the release artifact without manually searching the JSON.
