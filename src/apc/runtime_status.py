"""Public runtime status code records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


IMPLEMENTED = "implemented"
PLANNED = "planned"
SKIPPED = "skipped"
FAILED = "failed"
UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class RuntimeStatusCode:
    """One stable public runtime status code."""

    code: str
    category: str
    description: str
    terminal: bool

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("RuntimeStatusCode.code must not be empty")
        if self.code != self.code.lower():
            raise ValueError("RuntimeStatusCode.code must be lowercase")
        if not self.category:
            raise ValueError("RuntimeStatusCode.category must not be empty")
        if not self.description:
            raise ValueError("RuntimeStatusCode.description must not be empty")


def default_runtime_status_codes() -> tuple[RuntimeStatusCode, ...]:
    """Return stable status code records used by public runtime reports."""

    return (
        RuntimeStatusCode(
            code=IMPLEMENTED,
            category="availability",
            description="Step or operator is available in the current public runtime.",
            terminal=False,
        ),
        RuntimeStatusCode(
            code=PLANNED,
            category="availability",
            description="Step or operator is declared but not implemented yet.",
            terminal=False,
        ),
        RuntimeStatusCode(
            code=SKIPPED,
            category="execution",
            description="Step was intentionally skipped for the current evidence run.",
            terminal=False,
        ),
        RuntimeStatusCode(
            code=FAILED,
            category="execution",
            description="Step failed during the current evidence run.",
            terminal=True,
        ),
        RuntimeStatusCode(
            code=UNAVAILABLE,
            category="environment",
            description="Step cannot run because a required backend or device is unavailable.",
            terminal=False,
        ),
    )


def runtime_status_code_map(
    codes: tuple[RuntimeStatusCode, ...] | None = None,
) -> dict[str, RuntimeStatusCode]:
    """Return status code records keyed by stable code."""

    rows = codes if codes is not None else default_runtime_status_codes()
    return {row.code: row for row in rows}


def is_runtime_status_code(code: str, codes: tuple[RuntimeStatusCode, ...] | None = None) -> bool:
    """Return whether code is a known public runtime status code."""

    return code in runtime_status_code_map(codes)


def runtime_status_codes_to_dict(
    codes: tuple[RuntimeStatusCode, ...] | None = None,
) -> dict[str, Any]:
    """Serialize public runtime status codes into JSON-ready data."""

    rows = codes if codes is not None else default_runtime_status_codes()
    return {
        "schema": "apc.runtime_status_codes.v1",
        "codes": [
            {
                "code": row.code,
                "category": row.category,
                "description": row.description,
                "terminal": row.terminal,
            }
            for row in rows
        ],
        "notes": [
            "Status codes are factual runtime evidence labels.",
            "Status codes do not imply solver API compatibility.",
        ],
    }
