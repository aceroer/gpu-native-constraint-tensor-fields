# Phase 13 Completion

Phase 13 adds narrow compatibility adapters.

Implemented deliverables:

```text
src/apc/adapters/
tests/test_adapters.py
docs/ADAPTERS.md
```

Acceptance checks:

```text
Adapters lower into native specs or CTIR.
Adapters do not bypass layout planning or operator registry.
Unsupported solver features fail loudly.
```

Verification:

```text
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests scripts
```

After Phase 13, the main decision is whether to deepen CUDA materialized runtime
coverage or broaden public problem-family adapters.
