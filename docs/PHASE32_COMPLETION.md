# Phase 32 Completion

Phase 32 attaches checked handoff fixtures to release artifact evidence.

## Added

```text
scripts/collect_release_artifacts.py examples field
docs/RELEASE_ARTIFACTS.md fixture schemas
tests/test_release_artifacts.py fixture schema checks
```

## Acceptance

```text
Release artifacts name the handoff fixture input and outputs.
Collector checks that fixture schemas are present.
Release notes keep the fixture route bounded to inspection evidence.
```

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest tests.test_release_artifacts -v
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
```

Observed result:

```text
tests/test_release_artifacts.py: OK
artifact collector status: ok
handoff_fixture_schemas: ok
```

The next phase should add a slightly richer public problem-family handoff
fixture while keeping the same checked-report and inspection-demo boundary.
