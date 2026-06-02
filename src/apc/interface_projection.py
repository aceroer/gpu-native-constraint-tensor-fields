"""Public interface projections from native runtime objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InterfaceProjection:
    """One public projection of a native runtime object."""

    kind: str
    reason: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("InterfaceProjection.kind must not be empty")
        if not self.reason:
            raise ValueError("InterfaceProjection.reason must not be empty")


def project_public_summary(kind: str, payload: dict[str, Any], *, reason: str) -> InterfaceProjection:
    """Wrap a JSON-ready payload as an explicit public projection."""

    if not isinstance(payload, dict):
        raise ValueError("projection payload must be a dictionary")
    return InterfaceProjection(kind=kind, reason=reason, payload=dict(payload))


def interface_projection_to_dict(projection: InterfaceProjection) -> dict[str, Any]:
    """Serialize an interface projection."""

    return {
        "projection": {
            "kind": projection.kind,
            "reason": projection.reason,
        },
        "payload": dict(projection.payload),
    }


def project_adapter_summary(payload: dict[str, Any]) -> InterfaceProjection:
    """Project an adapter result summary into the public API boundary."""

    return project_public_summary(
        "adapter_summary",
        payload,
        reason="adapter result projected from native problem, CTIR, layout, and registry",
    )


def project_runtime_summary(payload: dict[str, Any], *, reason: str) -> InterfaceProjection:
    """Project a runtime summary into the public API boundary."""

    return project_public_summary("runtime_summary", payload, reason=reason)
