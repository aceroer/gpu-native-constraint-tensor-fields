# Verify Release

Use the release verifier from the repository root:

```bash
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
```

The verifier emits:

```text
schema
status
mode
checks
```

Quick mode runs:

```text
compileall
quickstart smoke tests
public docs tests
CPU benchmark smoke
vector-native demo benchmark smoke
public terminology boundary scan
```

Full mode also runs the complete unittest suite:

```bash
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full.json
```

The verifier exits nonzero if any check fails.
