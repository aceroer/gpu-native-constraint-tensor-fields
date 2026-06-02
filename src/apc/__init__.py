"""APC public Python package."""

from .benchmark import BenchmarkConfig, run_benchmark, write_benchmark_report
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
from .io_json import load_problem_json, problem_to_json_dict, save_problem_json
from .layout import LayoutPlan, LayoutView, OperatorLayout, layout_summary, plan_layout
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
from .runtime_cpu import RuntimeConfig, RuntimeResult, run_repair, run_repair_from_json
from .spec import BinaryDomainSpec, LinearCSRSpec, ObjectiveSpec, ProblemSpec

__all__ = [
    "BinaryDomainSpec",
    "BenchmarkConfig",
    "CTIRProblem",
    "LedgerSpec",
    "LayoutPlan",
    "LayoutView",
    "LedgerRow",
    "LinearCSR",
    "LinearCSRSpec",
    "MoveBatch",
    "MaxSATClause",
    "MaxSATRepairResult",
    "MaxSATSpec",
    "ObjectiveSpec",
    "OperatorLayout",
    "OperatorSpec",
    "ProjectionSpec",
    "ProblemSpec",
    "RuntimeConfig",
    "RuntimeResult",
    "StateBatch",
    "VarDomain",
    "ViolationBatch",
    "ctir_json",
    "ctir_to_dict",
    "default_operator_registry",
    "eval_unsatisfied_clauses",
    "inspect_ctir",
    "layout_summary",
    "ledger_to_dicts",
    "load_problem_json",
    "load_maxsat_json",
    "lower_problem_to_ctir",
    "lower_maxsat_to_ctir",
    "maxsat_penalty",
    "problem_to_json_dict",
    "plan_layout",
    "run_repair",
    "run_repair_from_json",
    "run_maxsat_bitflip_repair",
    "run_benchmark",
    "run_cuda_benchmark_report",
    "registry_summary",
    "save_problem_json",
    "write_benchmark_report",
]
