#include "../include/apc_runtime.h"

#include <cuda_runtime.h>
#include <math.h>

// This file is intentionally small. It demonstrates how the theory stack is
// written as CUDA operators:
//
// 1. eval_linear_csr_kernel       relation-field reading
// 2. rectify_violation_kernel     rectifier / nonnegative boundary
// 3. reduce_penalty_kernel        ledger reduction
// 4. project_binary_kernel        projection / regulator
//
// A production version would add CUB reductions, row-length buckets, CSC
// incidence for bit-flip deltas, timing, and differential validation.

namespace {

cudaStream_t as_stream(void* stream) {
  return reinterpret_cast<cudaStream_t>(stream);
}

APC_Status sync_status(cudaError_t err) {
  if (err != cudaSuccess) {
    return APC_ERR_CUDA;
  }
  return APC_OK;
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
    response[candidate * linear.n_rows + row] = partial[0] - linear.rhs[row];
  }
}

__global__ void rectify_violation_kernel(
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
  const int8_t sense = linear.sense[row];

  double v = 0.0;
  if (sense == APC_SENSE_LE) {
    v = fmax(value, 0.0);
  } else if (sense == APC_SENSE_GE) {
    v = fmax(-value, 0.0);
  } else {
    v = fabs(value);
  }
  violation[idx] = v;
}

__global__ void reduce_penalty_kernel(
    APC_LinearCSR linear,
    int batch_size,
    const double* violation,
    double* penalty) {
  const int candidate = blockIdx.x;
  const int tid = threadIdx.x;

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

__global__ void project_binary_kernel(APC_StateBatch states) {
  const int idx = blockIdx.x * blockDim.x + threadIdx.x;
  const int total = states.batch_size * states.n_vars;
  if (idx >= total) {
    return;
  }
  states.x[idx] = states.x[idx] != 0 ? 1 : 0;
}

}  // namespace

extern "C" APC_Status apc_eval_linear_csr(APC_RuntimeCtx* ctx) {
  if (!ctx || !ctx->linear || !ctx->states || !ctx->violations) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const dim3 grid(ctx->states->batch_size, ctx->linear->n_rows);
  const int block = 128;
  const size_t shared_bytes = sizeof(double) * block;
  eval_linear_csr_kernel<<<grid, block, shared_bytes, as_stream(ctx->stream)>>>(
      *ctx->linear, *ctx->states, ctx->violations->response);
  return sync_status(cudaGetLastError());
}

extern "C" APC_Status apc_rectify_linear_violation(APC_RuntimeCtx* ctx) {
  if (!ctx || !ctx->linear || !ctx->violations) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const int total = ctx->violations->batch_size * ctx->violations->n_rows;
  const int block = 256;
  const int grid = (total + block - 1) / block;
  rectify_violation_kernel<<<grid, block, 0, as_stream(ctx->stream)>>>(
      *ctx->linear,
      ctx->violations->batch_size,
      ctx->violations->response,
      ctx->violations->violation);
  return sync_status(cudaGetLastError());
}

extern "C" APC_Status apc_reduce_weighted_penalty(APC_RuntimeCtx* ctx) {
  if (!ctx || !ctx->linear || !ctx->violations) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const int block = 128;
  const size_t shared_bytes = sizeof(double) * block;
  reduce_penalty_kernel<<<ctx->violations->batch_size, block, shared_bytes,
                          as_stream(ctx->stream)>>>(
      *ctx->linear,
      ctx->violations->batch_size,
      ctx->violations->violation,
      ctx->violations->penalty);
  return sync_status(cudaGetLastError());
}

extern "C" APC_Status apc_project_binary(APC_RuntimeCtx* ctx) {
  if (!ctx || !ctx->states) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const int total = ctx->states->batch_size * ctx->states->n_vars;
  const int block = 256;
  const int grid = (total + block - 1) / block;
  project_binary_kernel<<<grid, block, 0, as_stream(ctx->stream)>>>(*ctx->states);
  return sync_status(cudaGetLastError());
}

