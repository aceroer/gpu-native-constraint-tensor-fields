# Phase 24 Completion

Phase 24 adds release artifact normalization.

Implemented deliverables:

```text
docs/RELEASE_ARTIFACTS.md
tests/test_release_artifacts.py
scripts/collect_release_artifacts.py
```

Acceptance checks:

```text
Artifact schema names verifier, benchmarks, docs, tests, and commit hash.
Collector emits JSON-ready release evidence.
Release notes reference the artifact contract.
```

Verification:

```text
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.N --out /tmp/apc-release-artifacts.json
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
```

The next phase should prepare the first public tag candidate.
