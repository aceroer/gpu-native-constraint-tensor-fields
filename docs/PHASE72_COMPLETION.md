# Phase 72 Completion

Phase 72 added runtime CLI family routing for implemented public routes.

Deliverables completed:

```text
src/apc/cli.py
docs/QUICKSTART.md
tests/test_cli.py
docs/PHASE72_COMPLETION.md
```

Validation target:

```text
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair:. python3 -m unittest tests.test_cli -v
```

The `apc run` command now accepts `--family auto`, routes QUBO and MaxSAT specs
to their CPU reference paths, keeps binary MILP behavior intact, and returns a
structured JSON failure for unsupported family names.
