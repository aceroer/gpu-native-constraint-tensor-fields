#!/usr/bin/env python3
"""Probe the optional native host runtime route."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NATIVE_DIR = ROOT / "native"
DEFAULT_BUILD_DIR = Path("/tmp/apc-native-host-probe")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="probe_native_host.py")
    parser.add_argument("--build-dir", default=str(DEFAULT_BUILD_DIR), help="native probe build directory")
    parser.add_argument("--no-build", action="store_true", help="configure only, do not build")
    parser.add_argument("--out", help="optional JSON output path")
    args = parser.parse_args(argv)

    report = probe_native_host(build_dir=Path(args.build_dir), build=not args.no_build)
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["status"] == "failed" else 0


def probe_native_host(*, build_dir: Path = DEFAULT_BUILD_DIR, build: bool = True) -> dict[str, Any]:
    """Probe configure/build evidence for the optional native host route."""

    cmake = shutil.which("cmake")
    paths = {
        "native_dir": str(NATIVE_DIR),
        "build_dir": str(build_dir),
        "header": str(NATIVE_DIR / "include" / "apc_runtime.hpp"),
        "shim": str(NATIVE_DIR / "src" / "cpu_operator_shim.cpp"),
    }
    if cmake is None:
        return {
            "schema": "apc.native_host_probe.v1",
            "status": "unavailable",
            "reason": "cmake_not_found",
            "paths": paths,
            "steps": [],
            "notes": _notes(),
        }

    build_dir.mkdir(parents=True, exist_ok=True)
    steps: list[dict[str, Any]] = []
    configure_cmd = [
        cmake,
        "-S",
        str(NATIVE_DIR),
        "-B",
        str(build_dir),
        "-DAPC_ENABLE_NATIVE_HOST=ON",
    ]
    steps.append(_run_step("configure", configure_cmd))

    if _steps_ok(steps) and build:
        build_cmd = [cmake, "--build", str(build_dir)]
        steps.append(_run_step("build", build_cmd))
    elif build:
        steps.append(_skipped_step("build"))

    return {
        "schema": "apc.native_host_probe.v1",
        "status": "ok" if _steps_ok(steps) else "failed",
        "reason": None if _steps_ok(steps) else "native_probe_step_failed",
        "paths": paths,
        "steps": steps,
        "notes": _notes(),
    }


def _run_step(name: str, cmd: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": name,
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
    }


def _skipped_step(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "cmd": [],
        "returncode": None,
        "skipped": True,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def _steps_ok(steps: list[dict[str, Any]]) -> bool:
    return all(step.get("returncode") == 0 for step in steps)


def _notes() -> list[str]:
    return [
        "Native host probe is optional evidence only.",
        "The probe does not change Python runtime behavior.",
        "The probe does not imply solver API compatibility.",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
