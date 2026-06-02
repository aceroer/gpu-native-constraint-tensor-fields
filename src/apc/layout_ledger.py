"""Layout conversion cost ledger."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutCost:
    """One planned layout conversion cost."""

    source: str
    target: str
    elements_read: int
    elements_written: int
    reason: str


def layout_costs_to_dicts(costs: tuple[LayoutCost, ...]) -> list[dict[str, int | str]]:
    """Convert layout cost rows into JSON-friendly dictionaries."""

    return [
        {
            "source": cost.source,
            "target": cost.target,
            "elements_read": cost.elements_read,
            "elements_written": cost.elements_written,
            "reason": cost.reason,
        }
        for cost in costs
    ]
