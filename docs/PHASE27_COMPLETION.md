# Phase 27 Completion

Phase 27 adds a durable release archive handoff.

Implemented deliverables:

```text
docs/RELEASE_ARCHIVE.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_release_archive.py
```

Acceptance checks:

```text
Archive doc names the tag, verifier, artifact report, and benchmark evidence.
Archive doc records how to reproduce the release evidence.
Release notes keep current limits and next work visible.
```

Verification:

```text
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
git rev-parse v0.1.0-alpha.0^{commit}
```

The next phase should prepare the public cross-project handoff sketch.
