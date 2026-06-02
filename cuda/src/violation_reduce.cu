#include "apc_runtime.h"

#include <cuda_runtime.h>
#include <math.h>

namespace {

cudaStream_t as_stream(void* stream) {
  return reinterpret_cast<cudaStream_t>(stream);
}

APC_Status launch_status(cudaError_t err) {
  return err == cudaSuccess ? APC_OK : APC_ERR_CUDA;
}

bool valid_violation_ctx(const APC_RuntimeCtx* ctx) {
  return ctx && ctx->linear && ctx->violations && ctx->linear->rhs &&
         ctx->linear->sense && ctx->violations->response &&
         ctx->violations->violation && ctx->linear->n_rows > 0 &&
         ctx->violations->batch_size > 0 &&
         ctx->violations->n_rows == ctx->linear->n_rows;
}

bool valid_penalty_ctx(const APC_RuntimeCtx* ctx) {
  return valid_violation_ctx(ctx) && ctx->linear->weight &&
         ctx->violations->penalty;
}

__global__ void rectify_linear_violation_kernel(
    APC_LinearCSR linear,
    int batch_size,
    const double* response,
    double* violation) {
  const int idx = blockIdx.x * blockDim.x + threadIdx.x;
  const int total = batch_size * linear.n_rows;
  if (idx >= total) {
    return;
  }

  const int row = idx % linear.n_rows;
  const double value = response[idx];
  const double rhs = linear.rhs[row];
  const int8_t sense = linear.sense[row];

  double v = 0.0;
  if (sense == APC_SENSE_LE) {
    v = fmax(value - rhs, 0.0);
  } else if (sense == APC_SENSE_GE) {
    v = fmax(rhs - value, 0.0);
  } else {
    v = fabs(value - rhs);
  }
  violation[idx] = v;
}

__global__ void reduce_weighted_penalty_kernel(
    APC_LinearCSR linear,
    int batch_size,
    const double* violation,
    double* penalty) {
  const int candidate = blockIdx.x;
  const int tid = threadIdx.x;

  if (candidate >= batch_size) {
    return;
  }

  extern __shared__ double partial[];
  double sum = 0.0;
  for (int row = tid; row < linear.n_rows; row += blockDim.x) {
    sum += linear.weight[row] * violation[candidate * linear.n_rows + row];
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
    penalty[candidate] = partial[0];
  }
}

}  // namespace

extern "C" APC_Status apc_rectify_linear_violation(APC_RuntimeCtx* ctx) {
  if (!valid_violation_ctx(ctx)) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const int total = ctx->violations->batch_size * ctx->violations->n_rows;
  const int block = 256;
  const int grid = (total + block - 1) / block;
  rectify_linear_violation_kernel<<<grid, block, 0, as_stream(ctx->stream)>>>(
      *ctx->linear,
      ctx->violations->batch_size,
      ctx->violations->response,
      ctx->violations->violation);
  return launch_status(cudaGetLastError());
}

extern "C" APC_Status apc_reduce_weighted_penalty(APC_RuntimeCtx* ctx) {
  if (!valid_penalty_ctx(ctx)) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const int block = 128;
  const size_t shared_bytes = sizeof(double) * block;
  reduce_weighted_penalty_kernel<<<ctx->violations->batch_size, block, shared_bytes,
                                   as_stream(ctx->stream)>>>(
      *ctx->linear,
      ctx->violations->batch_size,
      ctx->violations->violation,
      ctx->violations->penalty);
  return launch_status(cudaGetLastError());
}
