# 0.4 Tag Execution

This document records the tag procedure for a 0.4 candidate. It does not claim
that a tag exists before the commands are run and verified.

## Required Evidence

```text
docs/RELEASE_CHECKLIST_0_4.md
docs/RELEASE_NOTES_0_4_DRAFT.md
docs/RELEASE_ARCHIVE_0_4.md
/tmp/apc-release-verify-full-0-4.json
/tmp/apc-release-artifacts-0-4.json
/tmp/apc-release-artifacts-summary-0-4.json
/tmp/apc-cuda-parity-report-0-4.json
/tmp/apc-runtime-debug-0-4.json
```

## Procedure

```bash
git status --short
python3 scripts/verify_public_release.py --full --out /tmp/apc-release-verify-full-0-4.json
python3 scripts/collect_release_artifacts.py --tag v0.4.0-alpha.N --out /tmp/apc-release-artifacts-0-4.json
python3 scripts/inspect_release_artifacts.py /tmp/apc-release-artifacts-0-4.json --out /tmp/apc-release-artifacts-summary-0-4.json
git tag -a v0.4.0-alpha.N -m "v0.4.0-alpha.N"
git show --stat v0.4.0-alpha.N
```

Before tagging, confirm that the artifact report commit matches the candidate
commit.

## Non-Goals

```text
No compatibility claim.
No performance claim.
No tag-final archive before tag verification.
```
