# Phase 1 Completion

Date: 2026-06-02

Phase 1 adds a small native JSON problem spec for the first supported target:
binary MILP feasibility repair.

## Scope

Phase 1 is complete when the repository can:

```text
Load a JSON spec into typed Python objects.
Reject malformed CSR structures.
Reject unsupported domain and row-sense values.
Round-trip one tiny spec without semantic loss.
```

## Delivered Files

Native spec package:

```text
src/apc/__init__.py
src/apc/spec.py
src/apc/io_json.py
```

Tiny public spec:

```text
examples/specs/binary_milp_tiny.json
```

Tests:

```text
tests/test_spec_loading.py
```

## Spec Shape

The first supported spec describes:

```text
binary domain
linear objective
linear CSR constraints
row senses: <=, >=, ==
nonnegative row weights
```

## Verification

Commands run from repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Observed result:

```text
Ran 5 tests
OK
```

Existing example regression commands:

```bash
cd examples/binary_milp_repair
PYTHONPATH=. python3 -m unittest discover -s tests
PYTHONPATH=. python3 run_demo.py
```

Observed result:

```text
Ran 3 tests
OK
best_state: (0, 1, 0)
best_objective: 1.0
best_penalty: 0.0
```

## Phase 1 Verdict

```text
complete
```

The repository is ready to move to Phase 2: CTIR core separation and inspection.

