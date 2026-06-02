# Phase 7 Completion

Phase 7 introduces device layout planning as a first-class step.

Implemented deliverables:

```text
src/apc/layout.py
src/apc/layout_ledger.py
docs/DEVICE_LAYOUTS.md
tests/test_layout_planner.py
```

Implemented layouts:

```text
state.candidate_major
state.variable_major
linear.csr
linear.csc
clause.csr
qubo.coo
violation.dense
violation.active_compact
```

Acceptance checks:

```text
Each runtime operator declares required input and output layouts.
Layout conversion costs are recorded in a layout ledger.
Dual views are explicit and marked as not materialized by default.
Layout summaries are printable from the CLI.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m apc.cli layout examples/specs/binary_milp_tiny.json --batch-size 4
PYTHONPATH=src python3 -m compileall src tests
```

The repository is ready to move to Phase 8: MaxSAT reading.
