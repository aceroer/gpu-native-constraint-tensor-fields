# Phase 12 Completion

Phase 12 adds host layout materialization.

Implemented deliverables:

```text
src/apc/layout_materialize.py
tests/test_layout_materialize.py
docs/LAYOUT_MATERIALIZATION.md
```

Acceptance checks:

```text
Candidate-major to variable-major conversion is deterministic.
CSR to CSC conversion preserves all nonzeros.
Conversion cost ledger matches materialized element counts.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests scripts
```

The next phase is compatibility adapters.
