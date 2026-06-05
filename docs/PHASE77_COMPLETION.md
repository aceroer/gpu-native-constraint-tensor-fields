# Phase 77 Completion

Phase 77 added public runtime debug tools for real-environment inspection.

Deliverables completed:

```text
src/apc/debug.py
scripts/inspect_runtime_debug.py
docs/DEBUGGING.md
docs/PUBLIC_HANDOFF.md
docs/RELEASE_ARTIFACTS.md
scripts/collect_release_artifacts.py
tests/test_runtime_debug.py
docs/PHASE77_COMPLETION.md
```

Validation target:

```text
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair:. python3 -m unittest tests.test_runtime_debug -v
```

The debug report emits `apc.runtime_debug_report.v1` and summarizes spec, CTIR,
layout, ledger, run artifacts, status codes, and CUDA availability. This also
establishes the post-0.4 rule that release routes keep an explicit debug-tooling
checkpoint.
