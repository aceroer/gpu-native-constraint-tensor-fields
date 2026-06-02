"""Benchmark sweep configuration contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VALID_BACKENDS = ("cpu", "cuda")
TIMING_FIELDS = (
    "kernel_time_s",
    "copy_time_s",
    "layout_conversion_time_s",
    "end_to_end_time_s",
)


@dataclass(frozen=True)
class BenchmarkSweepCase:
    """One benchmark sweep case."""

    name: str
    spec: str
    backend: str
    out: str
    max_iters: int = 8
    batch_size: int = 4
    seed: int = 0
    penalty_weight: float = 10.0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("sweep case name must not be empty")
        if not self.spec:
            raise ValueError(f"{self.name} spec must not be empty")
        if self.backend not in VALID_BACKENDS:
            raise ValueError(f"{self.name} backend must be cpu or cuda")
        if not self.out:
            raise ValueError(f"{self.name} output path must not be empty")
        if self.max_iters < 0:
            raise ValueError(f"{self.name} max_iters must be nonnegative")
        if self.batch_size <= 0:
            raise ValueError(f"{self.name} batch_size must be positive")
        if self.penalty_weight <= 0.0:
            raise ValueError(f"{self.name} penalty_weight must be positive")


@dataclass(frozen=True)
class BenchmarkSweepConfig:
    """JSON-ready benchmark sweep configuration."""

    name: str
    cases: tuple[BenchmarkSweepCase, ...]
    timing_fields: tuple[str, ...] = TIMING_FIELDS
    notes: tuple[str, ...] = (
        "Sweep configs define benchmark evidence inputs only.",
        "No performance claim is made without complete timing evidence.",
    )

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("sweep config name must not be empty")
        if not self.cases:
            raise ValueError("sweep config must include at least one case")
        names = [case.name for case in self.cases]
        if len(names) != len(set(names)):
            raise ValueError("sweep case names must be unique")
        if set(self.timing_fields) != set(TIMING_FIELDS):
            raise ValueError("sweep config must name all timing fields")


def benchmark_sweep_config_to_dict(config: BenchmarkSweepConfig) -> dict[str, Any]:
    """Serialize benchmark sweep config into JSON-ready data."""

    return {
        "schema": "apc.benchmark_sweep_config.v1",
        "name": config.name,
        "cases": [_case_to_dict(case) for case in config.cases],
        "timing_fields": list(config.timing_fields),
        "notes": list(config.notes),
    }


def benchmark_sweep_config_from_dict(payload: dict[str, Any]) -> BenchmarkSweepConfig:
    """Parse and validate a benchmark sweep config from JSON-ready data."""

    if payload.get("schema") != "apc.benchmark_sweep_config.v1":
        raise ValueError("unsupported benchmark sweep config schema")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("benchmark sweep config cases must be a list")
    return BenchmarkSweepConfig(
        name=_required_str(payload, "name"),
        cases=tuple(_case_from_dict(case) for case in cases),
        timing_fields=tuple(payload.get("timing_fields", ())),
        notes=tuple(str(note) for note in payload.get("notes", ())),
    )


def load_benchmark_sweep_config(path: str | Path) -> BenchmarkSweepConfig:
    """Load a benchmark sweep config JSON file."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("benchmark sweep config must be a JSON object")
    return benchmark_sweep_config_from_dict(payload)


def write_benchmark_sweep_config(config: BenchmarkSweepConfig, path: str | Path) -> None:
    """Write a benchmark sweep config JSON file."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(benchmark_sweep_config_to_dict(config), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _case_to_dict(case: BenchmarkSweepCase) -> dict[str, Any]:
    return {
        "name": case.name,
        "spec": case.spec,
        "backend": case.backend,
        "out": case.out,
        "max_iters": case.max_iters,
        "batch_size": case.batch_size,
        "seed": case.seed,
        "penalty_weight": case.penalty_weight,
    }


def _case_from_dict(payload: Any) -> BenchmarkSweepCase:
    if not isinstance(payload, dict):
        raise ValueError("benchmark sweep case must be an object")
    return BenchmarkSweepCase(
        name=_required_str(payload, "name"),
        spec=_required_str(payload, "spec"),
        backend=_required_str(payload, "backend"),
        out=_required_str(payload, "out"),
        max_iters=int(payload.get("max_iters", 8)),
        batch_size=int(payload.get("batch_size", 4)),
        seed=int(payload.get("seed", 0)),
        penalty_weight=float(payload.get("penalty_weight", 10.0)),
    )


def _required_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a nonempty string")
    return value
