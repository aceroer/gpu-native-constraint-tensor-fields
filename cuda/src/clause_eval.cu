#include "apc_runtime.h"

#include <cuda_runtime.h>

namespace {

cudaStream_t as_stream(void* stream) {
  return reinterpret_cast<cudaStream_t>(stream);
}

APC_Status launch_status(cudaError_t err) {
  return err == cudaSuccess ? APC_OK : APC_ERR_CUDA;
}

bool valid_clause_ctx(
    const APC_ClauseCSR* clauses,
    const APC_StateBatch* states,
    const APC_ClauseBatch* output) {
  return clauses && states && output && clauses->clause_ptr && clauses->lit_var &&
         clauses->lit_sign && states->x && output->unsatisfied &&
         clauses->n_clauses > 0 && clauses->n_vars > 0 && clauses->nnz >= 0 &&
         states->batch_size > 0 && states->n_vars == clauses->n_vars &&
         output->batch_size == states->batch_size &&
         output->n_clauses == clauses->n_clauses;
}

__global__ void eval_clause_csr_kernel(
    APC_ClauseCSR clauses,
    APC_StateBatch states,
    int32_t* unsatisfied) {
  const int candidate = blockIdx.x;
  const int clause = blockIdx.y;
  if (threadIdx.x != 0) {
    return;
  }

  bool satisfied = false;
  const int start = clauses.clause_ptr[clause];
  const int end = clauses.clause_ptr[clause + 1];
  for (int offset = start; offset < end; ++offset) {
    const int var = clauses.lit_var[offset];
    const int sign = clauses.lit_sign[offset];
    const int value = states.x[candidate * states.n_vars + var];
    if ((sign == 1 && value == 1) || (sign == -1 && value == 0)) {
      satisfied = true;
      break;
    }
  }
  unsatisfied[candidate * clauses.n_clauses + clause] = satisfied ? 0 : 1;
}

}  // namespace

extern "C" APC_Status apc_eval_clause_csr(
    const APC_ClauseCSR* clauses,
    const APC_StateBatch* states,
    APC_ClauseBatch* output,
    void* stream) {
  if (!valid_clause_ctx(clauses, states, output)) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const dim3 grid(states->batch_size, clauses->n_clauses);
  eval_clause_csr_kernel<<<grid, 1, 0, as_stream(stream)>>>(
      *clauses, *states, output->unsatisfied);
  return launch_status(cudaGetLastError());
}
