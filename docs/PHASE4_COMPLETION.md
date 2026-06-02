# Phase 4 Completion

Phase 4 adds a small command line interface for the public native workflow.

Implemented deliverables:

```text
src/apc/cli.py
pyproject.toml
tests/test_cli.py
```

Commands:

```text
apc validate examples/specs/binary_milp_tiny.json
apc inspect-ctir examples/specs/binary_milp_tiny.json
apc run examples/specs/binary_milp_tiny.json --backend cpu
apc ledger runs/latest/ledger.json
```

Acceptance checks:

```text
Invalid specs return a nonzero CLI exit code.
CTIR inspection prints a compact JSON summary.
CPU runs write a ledger file.
CPU runs report a best feasible candidate when found.
Ledger files can be summarized by the CLI.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m apc.cli validate examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli inspect-ctir examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli run examples/specs/binary_milp_tiny.json --backend cpu --ledger-out runs/latest/ledger.json
PYTHONPATH=src python3 -m apc.cli ledger runs/latest/ledger.json
```

The repository is ready to move to Phase 5: CUDA build skeleton.
