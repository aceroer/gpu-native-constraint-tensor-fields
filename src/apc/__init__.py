"""APC public Python package."""

from .adapters import AdapterResult, adapter_result_to_dict, lower_native_binary_milp_dict
from .benchmark import BenchmarkConfig, run_benchmark, write_benchmark_report
from .branch_tensor import (
    BranchRoute,
    BranchTensor,
    branch_tensor_from_state_pool,
    branch_tensor_summary,
    canonical_branch_keys,
    mask_branch_tensor,
)
from .cuda_benchmark import run_cuda_benchmark_report
from .ctir import (
    CTIRProblem,
    LedgerSpec,
    LinearCSR,
    MoveBatch,
    ProjectionSpec,
    StateBatch,
    VarDomain,
    ViolationBatch,
    ctir_to_dict,
)
from .inspect_ctir import ctir_json, inspect_ctir
from .interface_projection import (
    InterfaceProjection,
    interface_projection_to_dict,
    project_adapter_summary,
    project_public_summary,
    project_runtime_summary,
)
from .io_json import load_problem_json, problem_to_json_dict, save_problem_json
from .layout import LayoutPlan, LayoutView, OperatorLayout, layout_summary, plan_layout
from .layout_materialize import (
    ActiveViolationCompact,
    LinearCSC,
    MaterializedLayout,
    materialize_active_violations,
    materialize_linear_csc,
    materialize_variable_major,
)
from .ledger import LedgerRow, ledger_to_dicts
from .lowering import lower_problem_to_ctir
from .operator_registry import (
    OperatorSpec,
    default_operator_registry,
    registry_summary,
)
from .readings.maxsat import (
    MaxSATClause,
    MaxSATRepairResult,
    MaxSATSpec,
    eval_unsatisfied_clauses,
    load_maxsat_json,
    lower_maxsat_to_ctir,
    maxsat_penalty,
    run_maxsat_bitflip_repair,
)
from .reduction_gate import (
    ReductionConfig,
    ReductionGateResult,
    RouteDecision,
    reduce_branch_tensor,
    reduction_gate_summary,
)
from .runtime_cpu import RuntimeConfig, RuntimeResult, run_repair, run_repair_from_json
from .spec import BinaryDomainSpec, LinearCSRSpec, ObjectiveSpec, ProblemSpec
from .state_pool import (
    StatePool,
    initialize_state_pool,
    mask_state_pool,
    state_pool_summary,
    state_pool_with_scores,
)

__all__ = [
    "ActiveViolationCompact",
    "AdapterResult",
    "BinaryDomainSpec",
    "BranchRoute",
    "BranchTensor",
    "BenchmarkConfig",
    "CTIRProblem",
    "InterfaceProjection",
    "LedgerSpec",
    "LayoutPlan",
    "LayoutView",
    "LedgerRow",
    "LinearCSR",
    "LinearCSRSpec",
    "LinearCSC",
    "MaterializedLayout",
    "MoveBatch",
    "MaxSATClause",
    "MaxSATRepairResult",
    "MaxSATSpec",
    "ObjectiveSpec",
    "OperatorLayout",
    "OperatorSpec",
    "ProjectionSpec",
    "ProblemSpec",
    "ReductionConfig",
    "ReductionGateResult",
    "RouteDecision",
    "RuntimeConfig",
    "RuntimeResult",
    "StateBatch",
    "StatePool",
    "VarDomain",
    "ViolationBatch",
    "adapter_result_to_dict",
    "branch_tensor_from_state_pool",
    "branch_tensor_summary",
    "canonical_branch_keys",
    "ctir_json",
    "ctir_to_dict",
    "default_operator_registry",
    "eval_unsatisfied_clauses",
    "initialize_state_pool",
    "inspect_ctir",
    "interface_projection_to_dict",
    "layout_summary",
    "ledger_to_dicts",
    "load_problem_json",
    "load_maxsat_json",
    "lower_native_binary_milp_dict",
    "lower_problem_to_ctir",
    "lower_maxsat_to_ctir",
    "mask_branch_tensor",
    "mask_state_pool",
    "materialize_active_violations",
    "materialize_linear_csc",
    "materialize_variable_major",
    "maxsat_penalty",
    "problem_to_json_dict",
    "plan_layout",
    "project_adapter_summary",
    "project_public_summary",
    "project_runtime_summary",
    "reduce_branch_tensor",
    "reduction_gate_summary",
    "run_repair",
    "run_repair_from_json",
    "run_maxsat_bitflip_repair",
    "run_benchmark",
    "run_cuda_benchmark_report",
    "registry_summary",
    "save_problem_json",
    "state_pool_summary",
    "state_pool_with_scores",
    "write_benchmark_report",
]
