"""Validation helpers for the example."""

from __future__ import annotations

from .ctir import BinaryDomain, LinearCSR, StateBatch


def assert_binary_domain(batch: StateBatch, domain: BinaryDomain) -> None:
    for row, x in enumerate(batch.x):
        if len(x) != domain.n_vars:
            raise AssertionError(f"candidate {row} has wrong width")
        bad = [value for value in x if value not in (0, 1)]
        if bad:
            raise AssertionError(f"candidate {row} is not binary: {bad}")


def assert_nonnegative_violations(violations: list[list[float]]) -> None:
    for row, candidate in enumerate(violations):
        bad = [value for value in candidate if value < 0.0]
        if bad:
            raise AssertionError(f"candidate {row} has negative violations: {bad}")


def assert_linear_csr_sane(linear: LinearCSR) -> None:
    if any(col < 0 or col >= linear.n_vars for col in linear.col_idx):
        raise AssertionError("col_idx out of range")
    if any(weight < 0.0 for weight in linear.weight):
        raise AssertionError("weights must be nonnegative")

