import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARITY_DOC = ROOT / "docs" / "CUDA_OPERATOR_PARITY.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cuda_diff_utils import base_harness_prelude, compile_and_run_harness


class CUDAQUBOMoveScoreDifferentialTests(unittest.TestCase):
    def test_parity_doc_names_qubo_move_score_contract(self):
        text = PARITY_DOC.read_text(encoding="utf-8")

        self.assertIn("target_id: qubo_bitflip_score", text)
        self.assertIn("cuda/src/qubo_move_score.cu", text)
        self.assertIn("apc_score_qubo_bitflip_moves", text)
        self.assertIn("apc.runtime_qubo_cpu.score_qubo_bitflip_moves", text)
        self.assertIn("status: implemented", text)
        self.assertIn("implemented_phase: Phase 70", text)
        self.assertNotIn("speedup", text.lower())

    def test_qubo_move_scores_match_cpu_reference_values(self):
        source = base_harness_prelude() + r'''
int main() {
  const int batch_size = 4;
  const int n_vars = 3;
  const int nnz = 2;
  const double tol = 1e-9;
  const int total_moves = batch_size * n_vars;

  std::vector<double> linear = {1.0, -2.0, 0.5};
  std::vector<int32_t> qi = {0, 1};
  std::vector<int32_t> qj = {1, 2};
  std::vector<double> q = {1.25, -0.75};
  std::vector<int32_t> states = {
      0, 0, 0,
      0, 1, 0,
      0, 1, 1,
      1, 1, 1,
  };

  auto energy_for = [&](int candidate, int flip_var) {
    double energy = 0.0;
    for (int var = 0; var < n_vars; ++var) {
      int value = states[candidate * n_vars + var];
      if (var == flip_var) {
        value = 1 - value;
      }
      energy += linear[var] * static_cast<double>(value);
    }
    for (int term = 0; term < nnz; ++term) {
      int xi = states[candidate * n_vars + qi[term]];
      int xj = states[candidate * n_vars + qj[term]];
      if (qi[term] == flip_var) {
        xi = 1 - xi;
      }
      if (qj[term] == flip_var) {
        xj = 1 - xj;
      }
      energy += q[term] * static_cast<double>(xi * xj);
    }
    return energy;
  };

  std::vector<double> current_energy(batch_size, 0.0);
  for (int candidate = 0; candidate < batch_size; ++candidate) {
    current_energy[candidate] = energy_for(candidate, -1);
  }

  std::vector<int32_t> expected_bit(total_moves, 0);
  std::vector<double> expected_old(total_moves, 0.0);
  std::vector<double> expected_candidate(total_moves, 0.0);
  std::vector<int8_t> expected_improves(total_moves, 0);
  for (int candidate = 0; candidate < batch_size; ++candidate) {
    for (int bit = 0; bit < n_vars; ++bit) {
      const int index = candidate * n_vars + bit;
      expected_bit[index] = bit;
      expected_old[index] = current_energy[candidate];
      expected_candidate[index] = energy_for(candidate, bit);
      expected_improves[index] = expected_candidate[index] < expected_old[index] ? 1 : 0;
    }
  }

  double* d_linear = device_copy(linear);
  int32_t* d_qi = device_copy(qi);
  int32_t* d_qj = device_copy(qj);
  double* d_q = device_copy(q);
  int32_t* d_states = device_copy(states);
  double* d_current_energy = device_copy(current_energy);

  int32_t* d_bit_index = nullptr;
  double* d_old_score = nullptr;
  double* d_candidate_score = nullptr;
  int8_t* d_improves = nullptr;
  require_cuda(cudaMalloc(&d_bit_index, sizeof(int32_t) * total_moves), "bit malloc");
  require_cuda(cudaMalloc(&d_old_score, sizeof(double) * total_moves), "old malloc");
  require_cuda(cudaMalloc(&d_candidate_score, sizeof(double) * total_moves), "candidate malloc");
  require_cuda(cudaMalloc(&d_improves, sizeof(int8_t) * total_moves), "improves malloc");

  APC_QUBOCOO qubo = {n_vars, nnz, d_qi, d_qj, d_q, d_linear};
  APC_StateBatch state_batch = {batch_size, n_vars, d_states};
  APC_QUBOMoveScoreBatch output = {
      batch_size,
      n_vars,
      d_bit_index,
      d_old_score,
      d_candidate_score,
      d_improves,
  };

  require_status(
      apc_score_qubo_bitflip_moves(&qubo, &state_batch, d_current_energy, &output, nullptr),
      "qubo move scoring failed");
  require_cuda(cudaDeviceSynchronize(), "sync");

  std::vector<int32_t> actual_bit = host_copy(d_bit_index, total_moves);
  std::vector<double> actual_old = host_copy(d_old_score, total_moves);
  std::vector<double> actual_candidate = host_copy(d_candidate_score, total_moves);
  std::vector<int8_t> actual_improves = host_copy(d_improves, total_moves);

  for (int index = 0; index < total_moves; ++index) {
    require_ok(actual_bit[index] == expected_bit[index], "bit index mismatch");
    expect_close(actual_old[index], expected_old[index], tol, "old score mismatch");
    expect_close(
        actual_candidate[index],
        expected_candidate[index],
        tol,
        "candidate score mismatch");
    require_ok(actual_improves[index] == expected_improves[index], "improves mismatch");
  }
  std::printf("qubo_move_score ok\n");
  return 0;
}
'''
        output = compile_and_run_harness(
            self,
            source,
            ("src/qubo_move_score.cu",),
        )
        self.assertIn("qubo_move_score ok", output)


if __name__ == "__main__":
    unittest.main()
