#include "apc_runtime.h"

#include <cuda_runtime.h>

namespace {

cudaStream_t as_stream(void* stream) {
  return reinterpret_cast<cudaStream_t>(stream);
}

APC_Status launch_status(cudaError_t err) {
  return err == cudaSuccess ? APC_OK : APC_ERR_CUDA;
}

bool valid_linear_eval_ctx(const APC_RuntimeCtx* ctx) {
  return ctx && ctx->linear && ctx->states && ctx->violations &&
         ctx->linear->row_ptr && ctx->linear->col_idx && ctx->linear->coeff &&
         ctx->violations->response && ctx->states->x &&
         ctx->linear->n_rows > 0 && ctx->linear->n_vars > 0 &&
         ctx->linear->nnz >= 0 && ctx->states->batch_size > 0 &&
         ctx->states->n_vars == ctx->linear->n_vars &&
         ctx->violations->batch_size == ctx->states->batch_size &&
         ctx->violations->n_rows == ctx->linear->n_rows;
}

__global__ void eval_linear_csr_kernel(
    APC_LinearCSR linear,
    APC_StateBatch states,
    double* response) {
  const int candidate = blockIdx.x;
  const int row = blockIdx.y;
  const int tid = threadIdx.x;

  extern __shared__ double partial[];
  double sum = 0.0;

  const int start = linear.row_ptr[row];
  const int end = linear.row_ptr[row + 1];
  for (int offset = start + tid; offset < end; offset += blockDim.x) {
    const int col = linear.col_idx[offset];
    const int x = states.x[candidate * states.n_vars + col];
    sum += linear.coeff[offset] * static_cast<double>(x);
  }

  partial[tid] = sum;
  __syncthreads();

  for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) {
      partial[tid] += partial[tid + stride];
    }
    __syncthreads();
  }

  if (tid == 0) {
    response[candidate * linear.n_rows + row] = partial[0];
  }
}

}  // namespace

extern "C" APC_Status apc_eval_linear_csr(APC_RuntimeCtx* ctx) {
  if (!valid_linear_eval_ctx(ctx)) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const dim3 grid(ctx->states->batch_size, ctx->linear->n_rows);
  const int block = 128;
  const size_t shared_bytes = sizeof(double) * block;
  eval_linear_csr_kernel<<<grid, block, shared_bytes, as_stream(ctx->stream)>>>(
      *ctx->linear, *ctx->states, ctx->violations->response);
  return launch_status(cudaGetLastError());
}
