import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARITY_DOC = ROOT / "docs" / "CUDA_OPERATOR_PARITY.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cuda_diff_utils import base_harness_prelude, compile_and_run_harness


class CUDAQUBOEnergyDifferentialTests(unittest.TestCase):
    def test_parity_doc_names_qubo_energy_contract(self):
        text = PARITY_DOC.read_text(encoding="utf-8")

        self.assertIn("target_id: qubo_energy_eval", text)
        self.assertIn("cuda/src/qubo_energy.cu", text)
        self.assertIn("apc_eval_qubo_energy", text)
        self.assertIn("apc.runtime_qubo_cpu.eval_qubo_energy", text)
        self.assertIn("planned_phase: Phase 64", text)
        self.assertNotIn("speedup", text.lower())

    def test_qubo_energy_matches_cpu_reference_values(self):
        source = base_harness_prelude() + r'''
int main() {
  const int batch_size = 4;
  const int n_vars = 3;
  const int nnz = 2;
  const double tol = 1e-9;

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
  std::vector<double> expected(batch_size, 0.0);
  for (int b = 0; b < batch_size; ++b) {
    for (int v = 0; v < n_vars; ++v) {
      expected[b] += linear[v] * static_cast<double>(states[b * n_vars + v]);
    }
    for (int t = 0; t < nnz; ++t) {
      const int xi = states[b * n_vars + qi[t]];
      const int xj = states[b * n_vars + qj[t]];
      expected[b] += q[t] * static_cast<double>(xi * xj);
    }
  }

  double* d_linear = device_copy(linear);
  int32_t* d_qi = device_copy(qi);
  int32_t* d_qj = device_copy(qj);
  double* d_q = device_copy(q);
  int32_t* d_states = device_copy(states);
  double* d_energy = nullptr;
  require_cuda(cudaMalloc(&d_energy, sizeof(double) * expected.size()), "energy malloc");

  APC_QUBOCOO qubo = {n_vars, nnz, d_qi, d_qj, d_q, d_linear};
  APC_StateBatch state_batch = {batch_size, n_vars, d_states};

  require_status(apc_eval_qubo_energy(&qubo, &state_batch, d_energy, nullptr), "qubo energy failed");
  require_cuda(cudaDeviceSynchronize(), "sync");

  std::vector<double> actual = host_copy(d_energy, static_cast<int>(expected.size()));
  for (int i = 0; i < static_cast<int>(expected.size()); ++i) {
    expect_close(actual[i], expected[i], tol, "qubo energy mismatch");
  }
  std::printf("qubo_energy ok\n");
  return 0;
}
'''
        output = compile_and_run_harness(
            self,
            source,
            ("src/qubo_energy.cu",),
        )
        self.assertIn("qubo_energy ok", output)


if __name__ == "__main__":
    unittest.main()
