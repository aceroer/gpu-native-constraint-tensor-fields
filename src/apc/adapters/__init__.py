"""Compatibility adapters for narrow public inputs."""

from .native_dict import (
    AdapterResult,
    adapter_result_to_dict,
    lower_native_binary_milp_dict,
)

__all__ = [
    "AdapterResult",
    "adapter_result_to_dict",
    "lower_native_binary_milp_dict",
]
