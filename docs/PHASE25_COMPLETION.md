# Phase 25 Completion

Phase 25 prepares the first public tag candidate.

Implemented deliverables:

```text
docs/TAG_PREP.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_tag_prep.py
```

Acceptance checks:

```text
Tag prep references verifier and artifact collector outputs.
Release notes name the candidate tag and commit hash fields.
Tag prep keeps limits and non-goals visible.
```

Verification:

```text
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
```

The next phase should execute the first public tag only after evidence artifacts
are clean and the tag commit matches the artifact report.
