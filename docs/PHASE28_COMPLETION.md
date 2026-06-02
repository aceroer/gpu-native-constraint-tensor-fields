# Phase 28 Completion

Phase 28 adds the public cross-project handoff sketch.

Implemented deliverables:

```text
docs/CROSS_PROJECT_HANDOFF.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_cross_project_handoff.py
```

Acceptance checks:

```text
Handoff sketch names the GPU release tag and artifact schema.
Handoff sketch names stable public entry points without private terminology.
Release notes describe the next cross-project route without claiming compatibility.
```

Verification:

```text
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
```

The next phase should prepare a public adapter sketch.
