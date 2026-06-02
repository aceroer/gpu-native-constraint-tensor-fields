# Phase 31 Completion

Phase 31 archives checked handoff demo fixtures.

## Added

```text
examples/handoff/vagent_apc_handoff_report.v1.json
examples/handoff/apc_handoff_check.v1.json
examples/handoff/apc_checked_handoff_demo.v1.json
tests/test_checked_handoff_fixtures.py
```

## Acceptance

```text
Fixture source input uses vagent.apc_handoff_report.v1.
Fixture checked output uses apc.cross_project_handoff_check.v1.
Fixture demo output uses apc.checked_handoff_runtime_demo.v1.
Fixture route remains an inspection demo and avoids claiming runtime compatibility.
```

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest tests.test_checked_handoff_fixtures -v
```

Observed result:

```text
Ran 4 tests
OK
```

The next phase should attach the fixture-backed handoff demo to release evidence
collection so release artifacts can name the fixed input/output pair directly.
