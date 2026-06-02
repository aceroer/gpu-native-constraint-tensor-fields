# Phase 17 Completion

Phase 17 adds interface projection boundaries.

Implemented deliverables:

```text
src/apc/interface_projection.py
tests/test_interface_projection.py
docs/INTERFACE_PROJECTION.md
```

Acceptance checks:

```text
Runtime state is not treated as the public API shape.
Each public output includes a projection reason.
Adapters and summaries use projection helpers.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests scripts
```

The next phase is vector-native repair demo bridge.
