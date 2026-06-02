"""Compatibility aliases for the example.

The example now uses the public CTIR objects from `src/apc` instead of carrying
its own duplicate structures.
"""

from __future__ import annotations

from dataclasses import dataclass

from apc.ctir import LinearCSR, StateBatch
from apc.spec import BinaryDomainSpec as BinaryDomain


@dataclass(frozen=True)
class RepairConfig:
    """Controls the repair feedback loop."""

    max_iters: int = 16
    lambda_penalty: float = 10.0
    objective_weight: float = 1.0
