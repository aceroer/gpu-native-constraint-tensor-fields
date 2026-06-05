#include "apc_runtime.h"

#include <cuda_runtime.h>

namespace {

cudaStream_t as_stream(void* stream) {
  return reinterpret_cast<cudaStream_t>(stream);
}

APC_Status launch_status(cudaError_t err) {
  return err == cudaSuccess ? APC_OK : APC_ERR_CUDA;
}

bool valid_qubo_ctx(
    const APC_QUBOCOO* qubo,
    const APC_StateBatch* states,
    const double* energy) {
  return qubo && states && energy && qubo->i && qubo->j && qubo->q &&
         qubo->linear && states->x && qubo->n_vars > 0 && qubo->nnz >= 0 &&
         states->batch_size > 0 && states->n_vars == qubo->n_vars;
}

__global__ void eval_qubo_energy_kernel(
    APC_QUBOCOO qubo,
    APC_StateBatch states,
    double* energy) {
  const int candidate = blockIdx.x;
  const int tid = threadIdx.x;

  extern __shared__ double partial[];
  double sum = 0.0;

  for (int var = tid; var < qubo.n_vars; var += blockDim.x) {
    const int x = states.x[candidate * states.n_vars + var];
    sum += qubo.linear[var] * static_cast<double>(x);
  }
  for (int term = tid; term < qubo.nnz; term += blockDim.x) {
    const int xi = states.x[candidate * states.n_vars + qubo.i[term]];
    const int xj = states.x[candidate * states.n_vars + qubo.j[term]];
    sum += qubo.q[term] * static_cast<double>(xi * xj);
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
    energy[candidate] = partial[0];
  }
}

}  // namespace

extern "C" APC_Status apc_eval_qubo_energy(
    const APC_QUBOCOO* qubo,
    const APC_StateBatch* states,
    double* energy,
    void* stream) {
  if (!valid_qubo_ctx(qubo, states, energy)) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const int block = 128;
  const size_t shared_bytes = sizeof(double) * block;
  eval_qubo_energy_kernel<<<states->batch_size, block, shared_bytes, as_stream(stream)>>>(
      *qubo, *states, energy);
  return launch_status(cudaGetLastError());
}
