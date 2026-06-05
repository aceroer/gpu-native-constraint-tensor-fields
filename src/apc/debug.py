"""Runtime debug report helpers."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .inspect_ctir import inspect_ctir
from .io_json import load_problem_json
from .layout import layout_summary, plan_layout
from .lowering import lower_problem_to_ctir
from .readings.maxsat import load_maxsat_json, lower_maxsat_to_ctir
from .readings.qubo import load_qubo_json, lower_qubo_to_ctir
from .runtime_status import runtime_status_codes_to_dict


DEBUG_SCHEMA = "apc.runtime_debug_report.v1"


def inspect_runtime_debug(
    *,
    spec: str | Path,
    ledger: str | Path | None = None,
    artifact_dir: str | Path | None = None,
    release_artifacts: str | Path | None = None,
    batch_size: int = 4,
) -> dict[str, Any]:
    """Return a JSON-ready debug report for one public runtime target."""

    spec_path = Path(spec)
    try:
        family = _problem_family(spec_path)
        ctir = _lower_for_family(spec_path, family, batch_size=batch_size)
        ctir_summary = inspect_ctir(ctir)
        layout = layout_summary(plan_layout(ctir))
        status = "ok"
        reason = None
    except Exception as exc:
        family = "unknown"
        ctir_summary = {}
        layout = {}
        status = "failed"
        reason = str(exc)

    cuda = cuda_debug()
    return {
        "schema": DEBUG_SCHEMA,
        "status": status,
        "reason": reason,
        "spec": _spec_debug(spec_path, family),
        "ctir": ctir_summary,
        "layout": layout,
        "ledger": _ledger_debug(Path(ledger)) if ledger else _empty_ledger_debug(),
        "run_artifacts": _artifact_debug(Path(artifact_dir)) if artifact_dir else _empty_artifact_debug(),
        "status_codes": runtime_status_codes_to_dict(),
        "cuda": cuda,
        "beta_checkpoint": _beta_checkpoint(
            cuda=cuda,
            status=status,
            release_artifacts=Path(release_artifacts) if release_artifacts else None,
        ),
        "notes": [
            "Runtime debug reports are factual inspection evidence.",
            "Reports avoid local absolute paths in public fields.",
            "Failure records should include enough context to reproduce tiny fixture failures.",
        ],
    }


def cuda_debug() -> dict[str, Any]:
    """Return CUDA debug facts without requiring CUDA to exist."""

    nvcc = shutil.which("nvcc")
    nvidia_smi = shutil.which("nvidia-smi")
    driver_version = None
    device_name = None
    driver_model = None
    device_available = False
    device_reason = "nvidia-smi not found"
    if nvidia_smi is not None:
        completed = subprocess.run(
            [nvidia_smi, "-L"],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            device_available = True
            device_reason = None
        else:
            device_reason = completed.stderr.strip() or "no CUDA device listed"
        query = subprocess.run(
            [
                nvidia_smi,
                "--query-gpu=name,driver_version,driver_model.current",
                "--format=csv,noheader",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if query.returncode == 0 and query.stdout.strip():
            fields = [field.strip() for field in query.stdout.splitlines()[0].split(",")]
            if len(fields) >= 1:
                device_name = fields[0] or None
            if len(fields) >= 2:
                driver_version = fields[1] or None
            if len(fields) >= 3 and fields[2] and fields[2].upper() != "N/A":
                driver_model = fields[2]
    if nvcc is None:
        skip_reason = "nvcc not found"
    elif not device_available:
        skip_reason = device_reason
    else:
        skip_reason = None
    return {
        "nvcc_available": nvcc is not None,
        "device_available": device_available,
        "device_name": device_name,
        "driver_version": driver_version,
        "driver_model": driver_model,
        "selected_arch": os.environ.get("APC_CUDA_ARCH", "").strip() or None,
        "skip_reason": skip_reason,
    }


def _beta_checkpoint(
    *,
    cuda: dict[str, Any],
    status: str,
    release_artifacts: Path | None,
) -> dict[str, Any]:
    return {
        "schema": "apc.runtime_debug_beta_checkpoint.v1",
        "compute_mode": _compute_mode(cuda),
        "host_role": _host_role(cuda),
        "host_compiler_readiness": _host_compiler_readiness(cuda),
        "cuda_differential_test_status": _cuda_differential_test_status(cuda),
        "release_artifact_status": _release_artifact_status(release_artifacts),
        "pci_hal_boundary_status": _pci_hal_boundary_status(),
        "runtime_debug_status": status,
    }


def _compute_mode(cuda: dict[str, Any]) -> str:
    driver_model = str(cuda.get("driver_model") or "").strip().lower()
    if "tcc" in driver_model:
        return "tcc"
    if "wddm" in driver_model:
        return "wddm"
    if cuda.get("device_available"):
        return "headless_cuda_or_driver_default"
    return "cuda_unavailable"


def _host_role(cuda: dict[str, Any]) -> str:
    override = os.environ.get("APC_HOST_ROLE", "").strip()
    if override in {"compute_core", "orchestration_layer"}:
        return override
    if cuda.get("device_available") and shutil.which("nvcc"):
        return "compute_core"
    return "orchestration_layer"


def _host_compiler_readiness(cuda: dict[str, Any]) -> dict[str, Any]:
    system = platform.system().lower()
    cxx = shutil.which("c++") or shutil.which("g++") or shutil.which("clang++")
    msvc = shutil.which("cl")
    cmake = shutil.which("cmake")
    if system == "windows":
        host_compiler = msvc
        host_compiler_name = "cl"
    else:
        host_compiler = cxx
        host_compiler_name = "cxx"
    missing = []
    if not cuda.get("nvcc_available"):
        missing.append("nvcc")
    if host_compiler is None:
        missing.append(host_compiler_name)
    if cmake is None:
        missing.append("cmake")
    if not missing:
        status = "ready"
    elif cuda.get("nvcc_available") or host_compiler is not None or cmake is not None:
        status = "partial"
    else:
        status = "missing"
    return {
        "status": status,
        "platform": platform.system() or "unknown",
        "nvcc_available": bool(cuda.get("nvcc_available")),
        "host_compiler": host_compiler_name,
        "host_compiler_available": host_compiler is not None,
        "cmake_available": cmake is not None,
        "missing": missing,
    }


def _cuda_differential_test_status(cuda: dict[str, Any]) -> dict[str, Any]:
    if cuda.get("nvcc_available") and cuda.get("device_available"):
        return {
            "status": "available",
            "reason": None,
            "required_surface": "tests/cuda differential parity",
        }
    return {
        "status": "skipped",
        "reason": cuda.get("skip_reason") or "CUDA differential tests unavailable in this environment",
        "required_surface": "tests/cuda differential parity",
    }


def _release_artifact_status(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"status": "not_requested", "name": None}
    if not path.exists():
        return {"status": "missing", "name": path.name}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"status": "failed", "name": path.name, "reason": str(exc)}
    return {
        "status": payload.get("status", "unknown") if isinstance(payload, dict) else "unknown",
        "name": path.name,
        "schema": payload.get("schema") if isinstance(payload, dict) else None,
    }


def _pci_hal_boundary_status() -> dict[str, Any]:
    return {
        "status": "sketch",
        "cpu_hardware_contract": "PCI/PCIe enumeration",
        "hal_role": "normalize WDDM, TCC, and Linux kernel-device differences",
        "device_control_owner": "target CUDAOS layer above checked HAL",
        "bar_register_policy": "evidence surface only until a checked HAL exists",
        "restricted_control_policy": "vendor/customer agreement before restricted hardware-control development",
    }


def _problem_family(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("spec must be a JSON object")
    problem_type = payload.get("problem_type")
    if problem_type == "qubo":
        return "qubo"
    if problem_type == "weighted_maxsat":
        return "maxsat"
    constraints = payload.get("constraints")
    if isinstance(constraints, dict) and "linear_csr" in constraints:
        return "binary_milp"
    raise ValueError(f"unsupported debug problem_type: {problem_type}")


def _lower_for_family(path: Path, family: str, *, batch_size: int):
    if family == "qubo":
        return lower_qubo_to_ctir(load_qubo_json(path), batch_size=batch_size)
    if family == "maxsat":
        return lower_maxsat_to_ctir(load_maxsat_json(path), batch_size=batch_size)
    if family == "binary_milp":
        return lower_problem_to_ctir(load_problem_json(path), batch_size=batch_size)
    raise ValueError(f"unsupported debug family: {family}")


def _spec_debug(path: Path, family: str) -> dict[str, Any]:
    return {
        "name": path.name,
        "problem_family": family,
        "exists": path.exists(),
    }


def _ledger_debug(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "missing", "name": path.name, "row_count": 0, "last": None}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"status": "failed", "name": path.name, "reason": str(exc), "row_count": 0, "last": None}
    rows = payload.get("ledger") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {"status": "missing", "name": path.name, "row_count": 0, "last": None}
    return {
        "status": "ok",
        "name": path.name,
        "row_count": len(rows),
        "last": rows[-1] if rows else None,
    }


def _artifact_debug(path: Path) -> dict[str, Any]:
    expected = ("input.json", "result.json", "ledger.json", "timings.json", "metadata.json")
    if not path.exists():
        return {"status": "missing", "name": path.name, "files": []}
    files = sorted(item.name for item in path.iterdir() if item.is_file())
    missing = [name for name in expected if name not in files]
    return {
        "status": "ok" if not missing else "partial",
        "name": path.name,
        "files": files,
        "missing": missing,
    }


def _empty_ledger_debug() -> dict[str, Any]:
    return {"status": "not_requested", "row_count": 0, "last": None}


def _empty_artifact_debug() -> dict[str, Any]:
    return {"status": "not_requested", "files": []}
