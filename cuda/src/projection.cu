#include "apc_runtime.h"

#include <cuda_runtime.h>

namespace {

cudaStream_t as_stream(void* stream) {
  return reinterpret_cast<cudaStream_t>(stream);
}

APC_Status launch_status(cudaError_t err) {
  return err == cudaSuccess ? APC_OK : APC_ERR_CUDA;
}

bool valid_projection_ctx(const APC_RuntimeCtx* ctx) {
  return ctx && ctx->states && ctx->states->x && ctx->states->batch_size > 0 &&
         ctx->states->n_vars > 0;
}

__global__ void project_binary_kernel(APC_StateBatch states) {
  const int idx = blockIdx.x * blockDim.x + threadIdx.x;
  const int total = states.batch_size * states.n_vars;
  if (idx >= total) {
    return;
  }
  states.x[idx] = states.x[idx] >= 1 ? 1 : 0;
}

}  // namespace

extern "C" APC_Status apc_project_binary(APC_RuntimeCtx* ctx) {
  if (!valid_projection_ctx(ctx)) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const int total = ctx->states->batch_size * ctx->states->n_vars;
  const int block = 256;
  const int grid = (total + block - 1) / block;
  project_binary_kernel<<<grid, block, 0, as_stream(ctx->stream)>>>(*ctx->states);
  return launch_status(cudaGetLastError());
}
