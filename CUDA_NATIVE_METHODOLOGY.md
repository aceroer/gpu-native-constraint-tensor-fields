# CUDA-Native Constraint Optimization Methodology

日期：2026-06-02

## 0. 核心原则

CUDA kernel 不是起点，而是结果。

组合优化/约束求解若直接从 kernel 开始，通常会很快陷入：

```text
访存不合并
warp divergence
atomic contention
shared memory bank conflict
host-device copy 混乱
调试困难
```

更稳的路线是先把数学约束对象降阶成 GPU 原生的张量/稀疏算子，再写 kernel：

```text
mathematical constraint object
→ constraint tensor IR
→ device memory layout
→ operator ABI
→ kernel specialization
→ runtime validation
```

这是一套从数学问题到 CUDA 实现的降阶方法论。

## 1. Layer 0：数学约束对象

首先不要问“怎么写 CUDA”，而要问：

```text
变量是什么？
约束是什么？
目标函数是什么？
哪些操作会反复发生？
哪些部分可以批量并行？
```

统一形式：

\[
x\in\Omega,\qquad C_i(x)\le0,\qquad f(x)\to\min.
\]

常见问题族：

```text
MILP / MIP:
  A x <= b, integrality, objective c^T x

MaxSAT:
  clauses, weights, unsatisfied penalty

QUBO:
  x^T Q x

CP-SAT:
  finite domains, boolean clauses, global constraints

Scheduling / routing:
  assignment, capacity, precedence, time windows
```

这一层只确定数学结构，不做 GPU 细节。

## 2. Layer 1：Constraint Tensor IR

第二步把数学对象变成中间表示：

```text
CTIR = Constraint Tensor Intermediate Representation
```

CTIR 不是建模语言，而是 GPU 可执行数据结构。

### 2.1 变量域

```c
typedef struct {
  int32_t n_vars;
  int8_t* var_type;   // binary, integer, continuous, categorical
  double* lb;
  double* ub;
} CTIR_VarDomain;
```

### 2.2 线性约束

```c
typedef struct {
  int32_t n_rows;
  int32_t nnz;
  int32_t* row_ptr;
  int32_t* col_idx;
  double*  coeff;
  double*  rhs;
  int8_t*  sense;     // <=, ==, >=
} CTIR_LinearCSR;
```

### 2.3 Clause 约束

```c
typedef struct {
  int32_t n_clauses;
  int32_t nnz_lits;
  int32_t* clause_ptr;
  int32_t* lit_idx;   // signed literal
  double*  weight;
} CTIR_ClauseCSR;
```

### 2.4 QUBO / graph energy

```c
typedef struct {
  int32_t n_vars;
  int32_t nnz;
  int32_t* i;
  int32_t* j;
  double*  q;
} CTIR_QUBOCOO;
```

### 2.5 状态批

```c
typedef struct {
  int32_t batch_size;
  int32_t n_vars;
  int32_t* x;         // shape [B, n] or layout-specific
} CTIR_StateBatch;
```

CTIR 的目的：

```text
让不同问题族共享同一个 GPU runtime。
```

## 3. Layer 2：Device Memory Layout

同一个 CTIR 进入 GPU 前，需要选择 device layout。

这一层决定性能。

### 3.1 Layout 选择

```text
CSR:
  稀疏线性约束，按 row 评估 Ax-b

CSC:
  按变量更新 row residual，适合 move delta

COO:
  graph / QUBO / pairwise interaction

ELL / SELL-C-sigma:
  row length 较规则时改善 coalesced access

Clause CSR:
  SAT / MaxSAT clause evaluation

Segmented arrays:
  scheduling / routing / global constraints
```

### 3.2 Batch 维度

两种常见布局：

```text
candidate-major:
  X[B, n]
  一个候选解连续存储

variable-major:
  X[n, B]
  一个变量在所有候选中的值连续存储
```

选择原则：

```text
若 kernel 按候选解评估完整约束，candidate-major 更自然。
若 kernel 按变量批量计算 move delta，variable-major 更利于 coalescing。
```

实际 runtime 应允许二者转换或维护双视图。

### 3.3 避免常见性能陷阱

```text
减少 host-device 往返
减少 global atomic
尽量让 warp 内执行路径一致
把频繁访问的小元数据放入 constant/shared memory
使用 block-level reduction 替代全局原子累加
对稀疏 row 进行长度分桶
对候选 batch 做 compact / deduplicate
```

## 4. Layer 3：Operator ABI

底层接口不应暴露 solver API，而应暴露算子 ABI。

核心算子：

```text
ConstraintEvalOp
ViolationReduceOp
MoveGenerateOp
MoveScoreOp
ProjectionOp
SelectionOp
DiversityOp
```

### 4.1 Runtime context

```c
typedef struct {
  void* device_problem;
  void* device_states;
  void* device_violations;
  void* device_moves;
  void* device_scores;
  void* device_rng;

  int32_t batch_size;
  int32_t n_vars;
  int32_t n_constraints;

  cudaStream_t stream;
} APC_RuntimeCtx;
```

### 4.2 Kernel-facing API

```c
APC_Status apc_eval_constraints(APC_RuntimeCtx* ctx);
APC_Status apc_reduce_violations(APC_RuntimeCtx* ctx);
APC_Status apc_generate_moves(APC_RuntimeCtx* ctx);
APC_Status apc_score_moves(APC_RuntimeCtx* ctx);
APC_Status apc_select_moves(APC_RuntimeCtx* ctx);
APC_Status apc_apply_projection(APC_RuntimeCtx* ctx);
APC_Status apc_reduce_best(APC_RuntimeCtx* ctx);
```

### 4.3 Problem-family registration

不同问题族注册不同算子：

```c
apc_register_eval_op(APC_LINEAR_CSR, linear_csr_eval_kernel);
apc_register_eval_op(APC_MAXSAT_CSR, maxsat_clause_eval_kernel);
apc_register_eval_op(APC_QUBO_COO, qubo_edge_eval_kernel);

apc_register_project_op(APC_PROJECT_BINARY, binary_project_kernel);
apc_register_project_op(APC_PROJECT_INTEGER, integer_project_kernel);
apc_register_project_op(APC_PROJECT_PERMUTATION, permutation_repair_kernel);

apc_register_move_op(APC_MOVE_BITFLIP, bitflip_move_kernel);
apc_register_move_op(APC_MOVE_INTEGER_STEP, integer_step_move_kernel);
apc_register_move_op(APC_MOVE_SWAP, swap_move_kernel);
```

## 5. Layer 4：Kernel Specialization

写 kernel 时不要追求“一核通吃”。应按问题族和 layout 专门化。

### 5.1 Linear CSR evaluation

目标：

\[
r=A x-b.
\]

适合 kernel：

```text
one block per row per candidate
warp-level row reduction
row length bucketization
optional ELL/SELL for regular rows
```

输出：

```text
residual[B, m]
violation[B, m]
penalty[B]
```

### 5.2 Move delta scoring

若 move 是 bit flip：

\[
x_j\leftarrow 1-x_j.
\]

不应重新计算所有约束，而应使用 CSC 或 incidence list 更新相关 row：

```text
affected_rows[j]
delta_row = coeff[row,j] * delta_x
delta_violation = new_violation - old_violation
```

GPU kernel：

```text
one block per candidate-variable move
iterate affected rows
reduce delta penalty
```

### 5.3 Projection

投影 kernel 应尽量简单、分支少：

```text
binary:
  x = x > threshold

integer:
  x = clamp(round(x), lb, ub)

bounded:
  x = min(max(x, lb), ub)

permutation:
  repair duplicates by segmented sort / conflict resolution
```

### 5.4 Selection

选择操作：

```text
top-k per candidate
best candidate per block
global incumbent reduction
diversity-aware selection
```

可先用成熟库：

```text
CUB reduction
Thrust sort/select
custom warp top-k for small K
```

## 6. Layer 5：Runtime Validation

CUDA 优化问题最容易出错，必须建立验证层。

### 6.1 CPU reference

每个 GPU kernel 都要有 CPU reference：

```python
cpu_eval_constraints(X, problem)
cpu_score_moves(X, moves, problem)
cpu_project(X, domains)
```

### 6.2 Differential testing

随机生成小实例：

```text
small n, small m, random constraints
random state batch
random moves
```

比较：

```text
CPU result == GPU result
within tolerance for floating point
```

### 6.3 Invariant checks

每轮检查：

```text
variables stay inside domain
integer variables remain integral
binary variables remain 0/1
violation is nonnegative
best objective never worsens when feasible incumbent is updated
projection does not introduce NaN/Inf
```

### 6.4 Performance counters

必须记录：

```text
kernel time
host-device copy time
occupancy
memory throughput
active batch size
violation decay
feasible candidate count
```

否则容易把数据搬运误认为 GPU 计算瓶颈。

## 7. 推荐实现路线

不要直接写全 CUDA runtime。建议四步走：

### Stage 1：CPU reference

```text
Python + NumPy/SciPy
MPS/WCNF parser
constraint evaluation
violation scoring
simple repair loop
```

目标：先证明 IR 和算子分解正确。

### Stage 2：GPU prototype

```text
CuPy / PyTorch / JAX
batched state tensor
sparse matrix evaluation
basic repair projection
```

目标：验证 GPU 原生张量流是否有速度和收敛优势。

### Stage 3：Custom kernels

```text
Triton:
  move scoring
  projection
  top-k

CUDA C++:
  irregular sparse constraint evaluation
  CSC delta update
  clause evaluation
```

目标：把瓶颈算子专门化。

### Stage 4：Runtime ABI

```text
C ABI
Python bindings
stream/memory pool
problem-family operator registry
benchmark harness
```

目标：形成可复用底层 runtime。

## 8. 最小内核计划

第一组 kernel 不要贪多：

```text
1. binary state batch initialization
2. linear CSR constraint evaluation
3. positive-part violation reduction
4. bit-flip move delta scoring
5. binary projection
6. best-candidate reduction
```

这六个 kernel 足以支撑一个二进制 MILP / MaxSAT repair prototype。

## 9. 设计口号

```text
Kernel is not the starting point.
Constraint tensorization is the starting point.
```

中文：

```text
CUDA kernel 不是起点，约束张量化才是起点。
```

这就是本方法论与普通 GPU 加速尝试的区别。

## 10. 后续文档

建议继续补：

```text
CTIR_SPEC.md
DEVICE_LAYOUTS.md
OPERATOR_ABI.md
KERNEL_PLAN.md
VALIDATION_PLAN.md
```

其中 `CTIR_SPEC.md` 和 `OPERATOR_ABI.md` 是最关键的两个底层文档。
