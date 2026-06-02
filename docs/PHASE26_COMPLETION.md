# Phase 26 Completion

Phase 26 executes the first public tag.

Implemented deliverables:

```text
docs/TAG_EXECUTION.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_tag_execution.py
```

Acceptance checks:

```text
Tag execution verifies the tag points to the collected commit hash.
Release notes record the final tag and evidence artifact paths.
Tag execution preserves the public language boundary.
```

Verification:

```text
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
python3 scripts/collect_release_artifacts.py --tag v0.1.0-alpha.0 --out /tmp/apc-release-artifacts.json
PYTHONPATH=src:examples/binary_milp_repair:examples/vector_state_repair python3 -m unittest discover -s tests -v
git rev-parse v0.1.0-alpha.0^{commit}
git ls-remote --tags origin v0.1.0-alpha.0
```

The next phase should prepare a durable release archive handoff.
