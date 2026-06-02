#!/usr/bin/env python3
"""List public handoff fixture sets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "examples" / "handoff"

FIXTURE_SETS = (
    {
        "name": "generic_task_pack",
        "problem_family": None,
        "source": "vagent_apc_handoff_report.v1.json",
        "checked": "apc_handoff_check.v1.json",
        "demo": "apc_checked_handoff_demo.v1.json",
    },
    {
        "name": "binary_milp",
        "problem_family": "binary_milp",
        "source": "vagent_binary_milp_handoff_report.v1.json",
        "checked": "apc_binary_milp_handoff_check.v1.json",
        "demo": "apc_binary_milp_checked_handoff_demo.v1.json",
    },
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="list_handoff_fixtures.py")
    parser.add_argument("--out", default=None, help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = list_handoff_fixtures()
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def list_handoff_fixtures() -> dict[str, Any]:
    """Return JSON-ready metadata for public handoff fixture sets."""

    fixtures = [_fixture_set_to_dict(item) for item in FIXTURE_SETS]
    return {
        "schema": "apc.handoff_fixture_index.v1",
        "status": "ok",
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
        "notes": [
            "Fixture sets are repository JSON inspection evidence only.",
            "This helper does not import paired projects or claim compatibility.",
        ],
    }


def _fixture_set_to_dict(item: dict[str, Any]) -> dict[str, Any]:
    source = _fixture_file(item["source"])
    checked = _fixture_file(item["checked"])
    demo = _fixture_file(item["demo"])
    return {
        "name": item["name"],
        "problem_family": item["problem_family"],
        "files": {
            "source": source,
            "checked": checked,
            "demo": demo,
        },
        "schemas": {
            "source": source["schema"],
            "checked": checked["schema"],
            "demo": demo["schema"],
        },
        "commands": {
            "check": (
                "PYTHONPATH=src python3 scripts/check_vagent_handoff.py "
                f"{source['path']} --out /tmp/{item['name']}-handoff-check.json"
            ),
            "demo": (
                "PYTHONPATH=src python3 scripts/run_checked_handoff_demo.py "
                f"/tmp/{item['name']}-handoff-check.json "
                f"--out /tmp/{item['name']}-checked-handoff-demo.json"
            ),
        },
    }


def _fixture_file(filename: str) -> dict[str, Any]:
    path = FIXTURE_DIR / filename
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": f"examples/handoff/{filename}",
        "exists": path.exists(),
        "schema": payload.get("schema") if isinstance(payload, dict) else None,
    }


if __name__ == "__main__":
    raise SystemExit(main())
