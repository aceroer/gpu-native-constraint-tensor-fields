#!/usr/bin/env python3
"""Inspect public CUDA parity targets and environment status."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARITY_DOC = ROOT / "docs" / "CUDA_OPERATOR_PARITY.md"
TIMING_FIELDS = (
    "kernel_time_s",
    "copy_time_s",
    "layout_conversion_time_s",
    "end_to_end_time_s",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="inspect_cuda_parity.py")
    parser.add_argument("--doc", default=str(PARITY_DOC), help="CUDA parity markdown document")
    parser.add_argument("--out", help="optional JSON output path")
    args = parser.parse_args(argv)

    report = inspect_cuda_parity(Path(args.doc))
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] != "failed" else 1


def inspect_cuda_parity(path: Path = PARITY_DOC) -> dict[str, Any]:
    """Return a JSON-ready CUDA parity report."""

    text = _read_text(path)
    if text is None:
        return _failed_report(path=path, reason="missing_cuda_parity_doc")

    env = cuda_environment()
    targets = [_target_report(target, env) for target in _parse_target_blocks(text)]
    status = "ok" if targets else "failed"
    return {
        "schema": "apc.cuda_parity_report.v1",
        "status": status,
        "source_path": str(path),
        "backend": "cuda",
        "target_count": len(targets),
        "targets": targets,
        "cuda_environment": env,
        "timing_fields": list(TIMING_FIELDS),
        "notes": [
            "CUDA parity inspection is factual status evidence only.",
            "Unavailable CUDA is reported explicitly and is not treated as hidden success.",
            "No performance claim is inferred from this report.",
        ],
    }


def cuda_environment() -> dict[str, Any]:
    """Return public CUDA environment facts without requiring CUDA to exist."""

    nvcc = shutil.which("nvcc")
    device = _cuda_device_summary()
    selected_arch = os.environ.get("APC_CUDA_ARCH", "").strip()
    if nvcc is None:
        availability = "unavailable"
        reason = "nvcc not found"
    elif not device["device_available"]:
        availability = "unavailable"
        reason = device["device_reason"]
    else:
        availability = "available"
        reason = None
    return {
        "availability": availability,
        "nvcc_available": nvcc is not None,
        "nvcc_path": nvcc,
        "device_available": device["device_available"],
        "device_reason": device["device_reason"],
        "selected_arch": selected_arch or None,
        "skip_reason": reason,
    }


def _target_report(target: dict[str, str], env: dict[str, Any]) -> dict[str, Any]:
    declared_status = target.get("status", "unknown")
    if declared_status == "planned":
        runtime_status = "planned"
        skip_reason = "target planned"
    elif env["availability"] == "available":
        runtime_status = declared_status
        skip_reason = None
    else:
        runtime_status = "unavailable"
        skip_reason = env["skip_reason"]
    return {
        "target_id": target.get("target_id", "unknown"),
        "operator": target.get("operator", "unknown"),
        "problem_family": target.get("problem_family", "unknown"),
        "backend": "cuda",
        "cuda_symbol": target.get("cuda_symbol", "unknown"),
        "cuda_source": target.get("cuda_source", "unknown"),
        "reference_route": target.get("cpu_reference", "unknown"),
        "test": target.get("test", "unknown"),
        "declared_status": declared_status,
        "status": runtime_status,
        "skip_reason": skip_reason,
        "timing_fields": list(TIMING_FIELDS),
    }


def _parse_target_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    in_block = False
    lines: list[str] = []
    for line in text.splitlines():
        if line.strip() == "```text":
            in_block = True
            lines = []
            continue
        if in_block and line.strip() == "```":
            block = _parse_key_value_lines(lines)
            if "target_id" in block:
                blocks.append(block)
            in_block = False
            continue
        if in_block:
            lines.append(line)
    return blocks


def _parse_key_value_lines(lines: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _cuda_device_summary() -> dict[str, Any]:
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi is None:
        return {"device_available": False, "device_reason": "nvidia-smi not found"}
    completed = subprocess.run(
        [nvidia_smi, "-L"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        reason = completed.stderr.strip() or "nvidia-smi device query failed"
        return {"device_available": False, "device_reason": reason}
    if not completed.stdout.strip():
        return {"device_available": False, "device_reason": "no CUDA device listed"}
    return {"device_available": True, "device_reason": None}


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _failed_report(*, path: Path, reason: str) -> dict[str, Any]:
    return {
        "schema": "apc.cuda_parity_report.v1",
        "status": "failed",
        "source_path": str(path),
        "backend": "cuda",
        "reason": reason,
        "target_count": 0,
        "targets": [],
        "cuda_environment": cuda_environment(),
        "timing_fields": list(TIMING_FIELDS),
        "notes": [
            "CUDA parity inspection is factual status evidence only.",
            "No performance claim is inferred from this report.",
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
