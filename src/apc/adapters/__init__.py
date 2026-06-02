"""Compatibility adapters for narrow public inputs."""

from .native_dict import (
    AdapterResult,
    adapter_result_to_dict,
    lower_native_binary_milp_dict,
)
from .vagent_handoff import (
    CHECK_SCHEMA,
    SOURCE_ARTIFACT_SCHEMA,
    SOURCE_REPORT_SCHEMA,
    VAgentHandoffMaterialization,
    check_vagent_handoff_file,
    check_vagent_handoff_report,
    load_vagent_handoff_report,
    write_handoff_check,
)

__all__ = [
    "AdapterResult",
    "CHECK_SCHEMA",
    "SOURCE_ARTIFACT_SCHEMA",
    "SOURCE_REPORT_SCHEMA",
    "VAgentHandoffMaterialization",
    "adapter_result_to_dict",
    "check_vagent_handoff_file",
    "check_vagent_handoff_report",
    "load_vagent_handoff_report",
    "lower_native_binary_milp_dict",
    "write_handoff_check",
]
