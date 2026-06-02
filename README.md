# GPU-Native Constraint Tensor Fields

日期：2026-06-02

Quickstart:

```bash
PYTHONPATH=src python3 -m apc.cli validate examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-bench.json --max-iters 2
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out /tmp/apc-vector-demo-bench.json
```

More first-run commands are in:

```text
docs/QUICKSTART.md
```

## 0. 定位

本目录用于整理一种 GPU 原生的组合优化/约束求解路线。

核心思想不是把传统 CPU 求解器的搜索树、回溯、剪枝强行搬到 GPU，而是从根部把问题改写成 GPU 擅长的批量张量计算：

```text
candidate batch
→ constraint response
→ violation tensor
→ repair direction
→ projection
→ feasible candidate extraction
```

对应成熟代码概念：

```text
state tensor
constraint matrix / sparse constraint graph
violation vector
batched local move evaluation
repair kernel
projection kernel
top-k selection
multi-start population
```

## 1. 目标问题族

第一阶段优先面向：

```text
MIP / MILP feasibility repair
CP-SAT-style constraint repair
MaxSAT / weighted MaxSAT local improvement
QUBO / HUBO energy minimization
scheduling / routing / packing
```

这些问题都有共同结构：

\[
x\in\Omega,\qquad C_i(x)\le 0,\qquad f(x)\to\min.
\]

代码中可统一为：

```python
StateBatch X          # shape: [B, n]
ConstraintData C      # sparse rows, clauses, graph edges, or propagators
ViolationBatch V      # shape: [B, m] or compressed [B, active_m]
ObjectiveBatch F      # shape: [B]
MoveBatch D           # shape: [B, K, move_dim]
```

其中：

- `B`: batch size / number of candidate states;
- `n`: variable count;
- `m`: constraint count;
- `K`: number of candidate moves per state.

## 2. 核心抽象

### 2.1 State Tensor

候选解不以单个节点处理，而以批量张量处理：

```python
X: int32[B, n]
```

常见编码：

```text
binary variables:      {0,1}
integer variables:     [lb, ub]
permutation variables: int32 permutation
mixed variables:       segmented tensor
```

### 2.2 Constraint Response

约束响应是批量算子：

```python
response = evaluate_constraints(X, C)
```

对 MILP：

\[
r=A x-b.
\]

对 SAT / MaxSAT：

\[
r_j = \mathbf 1\{\text{clause }j\text{ unsatisfied}\}.
\]

对 CP：

```text
response = domain violation / bound violation / global-constraint residual
```

### 2.3 Violation Tensor

违约量统一为非负张量：

\[
V(X)=\max(C(X),0).
\]

代码概念：

```python
V = positive_part(response)
penalty = weighted_sum(V)
energy = objective + lambda_ * penalty
```

### 2.4 Repair Direction

修复方向不是单路径搜索，而是批量生成候选 move：

```python
moves = propose_moves(X, V, C, rng)
delta_energy = evaluate_moves(X, moves, C)
```

常见 move：

```text
bit flip
integer +/- step
swap
segment reverse
rounding from LP solution
constraint-guided variable reset
large neighborhood destroy/repair
```

### 2.5 Projection Kernel

GPU 张量流更新后，需要投影回离散可行域或变量域：

```python
X_next = project_domains(X + step, bounds, integrality, permutation_rules)
```

投影类型：

```text
clamp to bounds
round to integer
binary threshold
permutation repair
one-hot normalization
capacity clipping
```

## 3. GPU 原生流水线

推荐第一版流水线：

```text
initialize batch
evaluate constraints
compute violation/energy
generate candidate moves
evaluate move deltas
select top-k moves per candidate
apply repair/projection
deduplicate / diversify
extract feasible incumbents
repeat
```

伪代码：

```python
def solve(problem, config):
    X = initialize_population(problem, config.batch_size)
    best = None

    for t in range(config.max_iters):
        R = evaluate_constraints(X, problem.constraints)
        V = positive_part(R)
        E = compute_energy(X, V, problem.objective)

        best = update_incumbent(best, X, V, E)

        M = propose_moves(X, V, problem, config.moves_per_state)
        dE = evaluate_move_deltas(X, M, problem)
        chosen = select_moves(dE, V, config)

        X = apply_moves(X, chosen)
        X = project_domains(X, problem.domains)
        X = diversify_if_stalled(X, E, t)

    return best
```

## 4. GPU Kernel 分解

第一版不必直接写完整求解器，可拆成几个 kernel：

```text
kernel_eval_linear_rows
kernel_eval_clause_violations
kernel_generate_moves
kernel_eval_bitflip_deltas
kernel_select_best_moves
kernel_apply_moves
kernel_project_domains
kernel_reduce_best_candidates
```

MIP/MILP 第一站：

```text
kernel_eval_sparse_Ax_minus_b
kernel_compute_row_violation
kernel_compute_variable_scores
kernel_parallel_rounding_repair
kernel_local_flip_repair
```

MaxSAT 第一站：

```text
kernel_eval_clauses
kernel_unsat_clause_variable_scores
kernel_parallel_flip_deltas
kernel_weighted_clause_penalty_reduce
```

## 5. 与现有成熟概念的对应

| 本路线概念 | 成熟工程概念 |
|---|---|
| 约束张量场 | batched constraint evaluation |
| 违约场 | violation vector / residual tensor |
| 修复流 | feasibility pump / repair heuristic |
| 点光源采样 | multi-start population / candidate particles |
| 光场重建 | surrogate scoring / learned or heuristic scoring |
| 投影闭合 | domain projection / rounding / repair |
| 能量下降 | local search / penalty minimization |
| 多尺度释放 | large neighborhood search / destroy-repair |

## 6. 第一阶段建议

最小可做版本不追求完整 MIP solver，而是做一个 GPU repair module：

```text
Input:
  MIP/MaxSAT/CP-SAT style instance
  initial candidate batch

Output:
  repaired feasible or lower-violation candidates
  incumbent objective
  violation decay curve
```

推荐先做两个 benchmark：

```text
1. MaxSAT bit-flip repair
2. MILP binary feasibility repair
```

原因：

- 二进制变量适合 GPU bit-level / vectorized 操作；
- 违约量容易定义；
- move delta 容易并行评估；
- benchmark 多，结果可复现。

## 7. 后续目录规划

```text
GPU/
  README.md
  docs/
    architecture.md
    mip_repair.md
    maxsat_repair.md
  src/
    apc_gpu/
      state.py
      constraints.py
      repair.py
      projection.py
      kernels/
  experiments/
    maxsat/
    mip/
  data/
  paper/
```

## 7.1 示例代码

当前有一个轻量示例库：

```text
examples/binary_milp_repair/
```

它展示 binary MILP feasibility repair 如何按以下层次写成代码：

```text
problem reading
-> CTIR-style data objects
-> CPU reference operators
-> CUDA operator ABI
-> specialized kernels
-> validation ledger
```

可运行 CPU reference：

```bash
cd examples/binary_milp_repair
PYTHONPATH=../../src:. python3 -m unittest discover -s tests
PYTHONPATH=../../src:. python3 run_demo.py
```

CUDA 写法示例：

```text
examples/binary_milp_repair/cuda/include/apc_runtime.h
examples/binary_milp_repair/cuda/src/binary_milp_kernels.cu
```

## 7.2 Native Problem Spec

当前已有第一版 native JSON spec loader：

```text
src/apc/spec.py
src/apc/io_json.py
examples/specs/binary_milp_tiny.json
tests/test_spec_loading.py
```

验证：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## 7.3 CTIR Core

当前已有执行侧 CTIR core：

```text
src/apc/ctir.py
src/apc/lowering.py
src/apc/inspect_ctir.py
tests/test_ctir_lowering.py
```

验证：

```bash
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests
```

## 7.4 CPU Runtime

当前已有第一版 CPU operator runtime：

```text
src/apc/operators_cpu.py
src/apc/runtime_cpu.py
src/apc/ledger.py
tests/test_runtime_cpu.py
```

验证：

```bash
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests
```

## 7.5 路线图

当前已有第一版 CLI：

```text
src/apc/cli.py
pyproject.toml
tests/test_cli.py
```

示例：

```bash
PYTHONPATH=src python3 -m apc.cli validate examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli inspect-ctir examples/specs/binary_milp_tiny.json
PYTHONPATH=src python3 -m apc.cli run examples/specs/binary_milp_tiny.json --backend cpu
PYTHONPATH=src python3 -m apc.cli ledger runs/latest/ledger.json
```

## 7.6 路线图

当前已有第一版可选 CUDA build skeleton：

```text
cuda/include/apc_runtime.h
cuda/src/linear_csr_eval.cu
cuda/src/violation_reduce.cu
cuda/src/projection.cu
cuda/CMakeLists.txt
tests/test_cuda_build_skeleton.py
```

无 CUDA 机器上的配置验证：

```bash
cmake -S cuda -B /tmp/apc-cuda-disabled -DAPC_ENABLE_CUDA=OFF
```

有 nvcc 时构建：

```bash
cmake -S cuda -B /tmp/apc-cuda-build -DAPC_ENABLE_CUDA=ON
cmake --build /tmp/apc-cuda-build
```

## 7.7 路线图

当前已有 CPU/GPU differential validation 测试：

```text
tests/cuda/test_linear_csr_eval.py
tests/cuda/test_projection.py
tests/cuda/test_penalty_reduce.py
```

无 `nvcc` 时这些测试会跳过；有 `nvcc` 时会编译临时 CUDA harness，
并把 GPU operator 输出和 CPU 期望值逐项比较。

验证：

```bash
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
```

## 7.8 路线图

当前已有 device layout planner：

```text
src/apc/layout.py
src/apc/layout_ledger.py
docs/DEVICE_LAYOUTS.md
tests/test_layout_planner.py
```

示例：

```bash
PYTHONPATH=src python3 -m apc.cli layout examples/specs/binary_milp_tiny.json
```

## 7.9 路线图

当前已有 weighted MaxSAT reading：

```text
src/apc/readings/maxsat.py
examples/specs/maxsat_tiny.json
tests/test_maxsat_cpu.py
cuda/src/clause_eval.cu
```

它把 tiny weighted MaxSAT 读入 `ClauseCSR`，并提供 CPU 未满足子句评估、
weighted penalty 和 bit-flip repair。CUDA clause eval 在有 `nvcc` 时由差分
测试覆盖。

验证：

```bash
PYTHONPATH=src:examples/binary_milp_repair python3 -m unittest discover -s tests -v
```

## 7.10 路线图

当前已有 benchmark harness：

```text
src/apc/benchmark.py
scripts/run_bench.py
docs/BENCHMARKING.md
benchmarks/
```

示例：

```bash
PYTHONPATH=src python3 scripts/run_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/latest.json
```

输出是 JSON，包含算法结果、ledger、layout conversion time、copy time、
kernel time 和 end-to-end time。CUDA backend 会单独报告；没有 copy-time
accounting 时不会声称 GPU speedup。

## 7.11 路线图

当前已有 operator registry：

```text
src/apc/operator_registry.py
docs/OPERATOR_REGISTRY.md
tests/test_operator_registry.py
```

示例：

```bash
PYTHONPATH=src python3 -m apc.cli operators
```

## 7.12 路线图

当前已有 CUDA benchmark timing：

```text
cuda/bench/
scripts/run_cuda_bench.py
docs/CUDA_BENCHMARK_TIMING.md
tests/cuda/test_cuda_bench_report.py
```

示例：

```bash
PYTHONPATH=src python3 scripts/run_cuda_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/latest_cuda.json
```

无 `nvcc` 或无 CUDA device 时会输出 unavailable JSON；有 CUDA 时会分开记录
copy time 与 kernel time，不输出 speedup ratio。

## 7.13 路线图

当前已有 layout materialization：

```text
src/apc/layout_materialize.py
docs/LAYOUT_MATERIALIZATION.md
tests/test_layout_materialize.py
```

它把 layout plan 中的部分非物化视图转换成实际 host 表示：

```text
state.candidate_major -> state.variable_major
linear.csr -> linear.csc
violation.dense -> violation.active_compact
```

## 7.14 路线图

当前已有 narrow compatibility adapter：

```text
src/apc/adapters/
docs/ADAPTERS.md
tests/test_adapters.py
```

adapter 只接受很窄的公开输入，并强制经过：

```text
ProblemSpec
-> CTIRProblem
-> layout plan
-> operator registry
```

不支持的 solver-oriented 功能会直接报错，不会静默绕过 native path。

## 7.15 路线图

当前已有 state pool runtime：

```text
src/apc/state_pool.py
docs/STATE_POOL.md
tests/test_state_pool.py
```

它把 candidate-major batch 提升为公开 runtime 对象：

```text
states
scores
uncertainty
alive_mask
metadata
```

## 7.16 路线图

当前已有 branch tensor / move routes：

```text
src/apc/branch_tensor.py
docs/BRANCH_TENSOR.md
tests/test_branch_tensor.py
```

它把 repair move 提升成固定形状的 route tensor：

```text
StatePool
-> BranchTensor
-> canonical branch keys
-> alive route mask
```

## 7.17 路线图

当前已有 deterministic reduction gate：

```text
src/apc/reduction_gate.py
docs/REDUCTION_GATE.md
tests/test_reduction_gate.py
```

它把 branch routes 归约成可解释的 selected actions：

```text
BranchTensor
-> route scoring
-> top-k selection
-> diversity penalty record
-> ledger-ready summary
```

## 7.18 路线图

当前已有 interface projection：

```text
src/apc/interface_projection.py
docs/INTERFACE_PROJECTION.md
tests/test_interface_projection.py
```

它把 native runtime object 投影成公开输出：

```text
native runtime state
-> projection kind
-> projection reason
-> public payload
```

## 7.19 路线图

当前已有 vector-native repair demo bridge：

```text
examples/vector_state_repair/
docs/VECTOR_NATIVE_REPAIR_DEMO.md
tests/test_vector_state_repair_demo.py
```

示例：

```bash
PYTHONPATH=src:examples/vector_state_repair python3 examples/vector_state_repair/run_demo.py
```

它输出 projected JSON report：

```text
projection
payload.metrics.branch_count
payload.metrics.selected_action_count
payload.metrics.success
```

## 7.20 路线图

当前已有 vector-native demo benchmark：

```text
scripts/run_vector_demo_bench.py
benchmarks/vector_native_report.example.json
tests/test_vector_demo_benchmark.py
```

示例：

```bash
PYTHONPATH=src:examples/vector_state_repair python3 scripts/run_vector_demo_bench.py examples/specs/binary_milp_tiny.json --out benchmarks/vector_native_report.latest.json
```

输出仍是 projected JSON report，并额外包含：

```text
payload.benchmark.runtime_path
payload.benchmark.timing
payload.benchmark.notes
```

## 7.21 路线图

当前已有 public quickstart packaging：

```text
docs/QUICKSTART.md
examples/README.md
benchmarks/README.md
tests/test_quickstart.py
```

quickstart 覆盖：

```text
validate
run
benchmark
vector-native demo benchmark
CUDA unavailable report
```

## 7.22 路线图

当前已有 public handoff checklist：

```text
docs/PUBLIC_HANDOFF.md
docs/RELEASE_NOTES_DRAFT.md
tests/test_public_docs.py
```

handoff 文档说明：

```text
stable first-run path
stable entry points
extension areas
testing expectations
benchmark expectations
public language boundary
```

## 7.23 路线图

当前已有 release verification script：

```text
scripts/verify_public_release.py
docs/VERIFY_RELEASE.md
tests/test_release_verifier.py
```

示例：

```bash
python3 scripts/verify_public_release.py --out /tmp/apc-release-verify.json
```

verifier 输出：

```text
schema
status
mode
checks
```

## 7.24 路线图

后续库建设路线见：

```text
ROADMAP.md
```

当前方向不是先兼容传统 solver API，而是先建立自己的轻量工具链：

```text
problem spec
-> CTIR lowering
-> device layout planning
-> operator registry
-> state pool
-> branch tensor
-> reduction gate
-> interface projection
-> vector-native demo
-> vector-native demo benchmark
-> repair runtime
-> validation ledger
-> benchmark harness
```

## 8. 研究判断

这条路线的关键不是“GPU 加速局部搜索”，而是：

```text
用 GPU 原生张量结构重新表达约束求解。
```

传统求解器的根结构是：

```text
branch
bound
propagate
backtrack
```

GPU 原生路线的根结构应是：

```text
batch
tensor response
violation field
parallel repair
projection
selection
```

因此第一目标不是替代成熟 CPU solver，而是建立一个可插拔的 GPU feasibility repair / primal heuristic layer。这个层一旦稳定，可以接入 MIP、CP-SAT、MaxSAT、QUBO、排程和路径规划等多个问题族。
