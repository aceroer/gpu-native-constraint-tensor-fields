#include "apc_runtime.h"

#include <cuda_runtime.h>

namespace {

cudaStream_t as_stream(void* stream) {
  return reinterpret_cast<cudaStream_t>(stream);
}

APC_Status launch_status(cudaError_t err) {
  return err == cudaSuccess ? APC_OK : APC_ERR_CUDA;
}

bool valid_qubo_move_score_ctx(
    const APC_QUBOCOO* qubo,
    const APC_StateBatch* states,
    const double* current_energy,
    const APC_QUBOMoveScoreBatch* output) {
  return qubo && states && current_energy && output && qubo->i && qubo->j &&
         qubo->q && qubo->linear && states->x && output->bit_index &&
         output->old_score && output->candidate_score && output->improves &&
         qubo->n_vars > 0 && qubo->nnz >= 0 && states->batch_size > 0 &&
         states->n_vars == qubo->n_vars &&
         output->batch_size == states->batch_size &&
         output->moves_per_state == qubo->n_vars;
}

__device__ double qubo_energy_for_flipped_bit(
    APC_QUBOCOO qubo,
    APC_StateBatch states,
    int candidate,
    int flip_var) {
  double energy = 0.0;
  for (int var = 0; var < qubo.n_vars; ++var) {
    int value = states.x[candidate * states.n_vars + var];
    if (var == flip_var) {
      value = 1 - value;
    }
    energy += qubo.linear[var] * static_cast<double>(value);
  }
  for (int term = 0; term < qubo.nnz; ++term) {
    int xi = states.x[candidate * states.n_vars + qubo.i[term]];
    int xj = states.x[candidate * states.n_vars + qubo.j[term]];
    if (qubo.i[term] == flip_var) {
      xi = 1 - xi;
    }
    if (qubo.j[term] == flip_var) {
      xj = 1 - xj;
    }
    energy += qubo.q[term] * static_cast<double>(xi * xj);
  }
  return energy;
}

__global__ void score_qubo_bitflip_moves_kernel(
    APC_QUBOCOO qubo,
    APC_StateBatch states,
    const double* current_energy,
    APC_QUBOMoveScoreBatch output) {
  const int total = states.batch_size * qubo.n_vars;
  const int index = blockIdx.x * blockDim.x + threadIdx.x;
  if (index >= total) {
    return;
  }

  const int candidate = index / qubo.n_vars;
  const int bit = index % qubo.n_vars;
  const double old_score = current_energy[candidate];
  const double candidate_score = qubo_energy_for_flipped_bit(qubo, states, candidate, bit);

  output.bit_index[index] = bit;
  output.old_score[index] = old_score;
  output.candidate_score[index] = candidate_score;
  output.improves[index] = candidate_score < old_score ? 1 : 0;
}

}  // namespace

extern "C" APC_Status apc_score_qubo_bitflip_moves(
    const APC_QUBOCOO* qubo,
    const APC_StateBatch* states,
    const double* current_energy,
    APC_QUBOMoveScoreBatch* output,
    void* stream) {
  if (!valid_qubo_move_score_ctx(qubo, states, current_energy, output)) {
    return APC_ERR_INVALID_ARGUMENT;
  }

  const int block = 128;
  const int total = states->batch_size * qubo->n_vars;
  const int grid = (total + block - 1) / block;
  score_qubo_bitflip_moves_kernel<<<grid, block, 0, as_stream(stream)>>>(
      *qubo, *states, current_energy, *output);
  return launch_status(cudaGetLastError());
}
