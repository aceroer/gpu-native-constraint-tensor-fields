# Phase 3 Completion

Phase 3 adds the CPU operator runtime for the public CTIR path.

Implemented deliverables:

```text
src/apc/operators_cpu.py
src/apc/runtime_cpu.py
src/apc/ledger.py
tests/test_runtime_cpu.py
```

Operator boundaries:

```text
eval_constraints
rectify_violations
reduce_penalty
generate_moves
score_moves
select_moves
apply_moves
apply_projection
reduce_best
record_metrics
```

Acceptance checks:

```text
JSON spec can run through a full CPU repair loop.
Ledger rows record objective, penalty, feasible count, and active violations.
Binary projection preserves domain invariants.
Fixed seeds produce deterministic CPU reference output.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m compileall src tests
```

The repository is ready to move to Phase 4: CLI.
