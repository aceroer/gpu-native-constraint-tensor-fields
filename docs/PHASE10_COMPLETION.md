# Phase 10 Completion

Phase 10 adds the public operator registry.

Implemented deliverables:

```text
src/apc/operator_registry.py
docs/OPERATOR_REGISTRY.md
tests/test_operator_registry.py
```

Acceptance checks:

```text
Operators list required input and output layouts.
CPU reference functions are named explicitly.
CUDA ABI symbols are listed when available.
Registry summaries are printable from the CLI.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m apc.cli operators
PYTHONPATH=src python3 -m compileall src tests scripts
```

The next phase is CUDA benchmark timing.
