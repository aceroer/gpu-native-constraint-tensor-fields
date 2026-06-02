# Phase 2 Completion

Date: 2026-06-02

Phase 2 separates user-facing problem specs from execution-facing CTIR.

## Scope

Phase 2 is complete when the repository can:

```text
Lower a problem spec into CTIR.
Serialize CTIR for inspection.
Catch CTIR shape and index errors.
Use public CTIR objects in the existing binary MILP example.
```

## Delivered Files

CTIR core:

```text
src/apc/ctir.py
src/apc/lowering.py
src/apc/inspect_ctir.py
```

Tests:

```text
tests/test_ctir_lowering.py
```

Example integration:

```text
examples/binary_milp_repair/apc_example/ctir.py
```

## CTIR Objects

The current CTIR core includes:

```text
VarDomain
LinearCSR
ClauseCSR
QUBOCOO
StateBatch
ViolationBatch
MoveBatch
ProjectionSpec
LedgerSpec
CTIRProblem
```

The first lowering path supports:

```text
binary MILP spec
-> VarDomain(binary)
-> ObjectiveLinear
-> LinearCSR
-> ProjectionSpec(binary)
-> MoveBatch(bit_flip)
-> LedgerSpec
```

## Verification

Commands run from repository root:

```bash
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests
```

Observed result:

```text
Ran 10 tests
OK
```

Existing example regression commands:

```bash
cd examples/binary_milp_repair
PYTHONPATH=/Users/aceroe/Documents/Code/GPU/src:. python3 -m unittest discover -s tests
PYTHONPATH=/Users/aceroe/Documents/Code/GPU/src:. python3 run_demo.py
```

Observed result:

```text
Ran 3 tests
OK
best_state: (0, 1, 0)
best_objective: 1.0
best_penalty: 0.0
```

## Phase 2 Verdict

```text
complete
```

The repository is ready to move to Phase 3: CPU operator runtime.

