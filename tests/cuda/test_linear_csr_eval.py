import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARITY_DOC = ROOT / "docs" / "CUDA_OPERATOR_PARITY.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cuda_diff_utils import base_harness_prelude, compile_and_run_harness


class CUDALinearCSREvalDifferentialTests(unittest.TestCase):
    def test_parity_doc_names_linear_csr_contract(self):
        text = PARITY_DOC.read_text(encoding="utf-8")

        self.assertIn("cuda/src/linear_csr_eval.cu", text)
        self.assertIn("apc_eval_linear_csr", text)
        self.assertIn("apc.operators_cpu.eval_constraints", text)
        self.assertIn("absolute_tolerance: 1e-9", text)
        self.assertIn("kernel_time_s", text)
        self.assertIn("copy_time_s", text)
        self.assertIn("layout_conversion_time_s", text)
        self.assertIn("end_to_end_time_s", text)
        self.assertNotIn("speedup", text.lower())

    def test_random_small_csr_matches_cpu_response(self):
        source = base_harness_prelude() + r'''
int main() {
  const int batch_size = 4;
  const int n_vars = 5;
  const int n_rows = 4;
  const double tol = 1e-9;

  std::mt19937 rng(17);
  std::uniform_int_distribution<int> col_dist(0, n_vars - 1);
  std::uniform_int_distribution<int> bit_dist(0, 1);
  std::uniform_real_distribution<double> coeff_dist(-2.0, 2.0);

  std::vector<int32_t> row_ptr = {0};
  std::vector<int32_t> col_idx;
  std::vector<double> coeff;
  for (int row = 0; row < n_rows; ++row) {
    const int row_nnz = 1 + (row % 3);
    for (int k = 0; k < row_nnz; ++k) {
      col_idx.push_back(col_dist(rng));
      coeff.push_back(coeff_dist(rng));
    }
    row_ptr.push_back(static_cast<int32_t>(col_idx.size()));
  }
  std::vector<double> rhs = {0.5, 1.0, -0.25, 2.0};
  std::vector<int8_t> sense = {APC_SENSE_LE, APC_SENSE_GE, APC_SENSE_EQ, APC_SENSE_LE};
  std::vector<double> weight = {1.0, 2.0, 0.5, 3.0};
  std::vector<int32_t> states(batch_size * n_vars, 0);
  for (int i = 0; i < static_cast<int>(states.size()); ++i) {
    states[i] = bit_dist(rng);
  }
  std::vector<double> expected(batch_size * n_rows, 0.0);
  for (int b = 0; b < batch_size; ++b) {
    for (int r = 0; r < n_rows; ++r) {
      double sum = 0.0;
      for (int p = row_ptr[r]; p < row_ptr[r + 1]; ++p) {
        sum += coeff[p] * static_cast<double>(states[b * n_vars + col_idx[p]]);
      }
      expected[b * n_rows + r] = sum;
    }
  }

  int32_t* d_row_ptr = device_copy(row_ptr);
  int32_t* d_col_idx = device_copy(col_idx);
  double* d_coeff = device_copy(coeff);
  double* d_rhs = device_copy(rhs);
  int8_t* d_sense = device_copy(sense);
  double* d_weight = device_copy(weight);
  int32_t* d_states = device_copy(states);
  double* d_response = nullptr;
  require_cuda(cudaMalloc(&d_response, sizeof(double) * expected.size()), "response malloc");

  APC_LinearCSR linear = {n_rows, n_vars, static_cast<int32_t>(col_idx.size()), d_row_ptr, d_col_idx, d_coeff, d_rhs, d_sense, d_weight};
  APC_StateBatch state_batch = {batch_size, n_vars, d_states};
  APC_ViolationBatch violations = {batch_size, n_rows, d_response, nullptr, nullptr};
  APC_RuntimeCtx ctx = {&linear, &state_batch, &violations, nullptr, nullptr, nullptr};

  require_status(apc_eval_linear_csr(&ctx), "eval failed");
  require_cuda(cudaDeviceSynchronize(), "sync");

  std::vector<double> actual = host_copy(d_response, static_cast<int>(expected.size()));
  for (int i = 0; i < static_cast<int>(expected.size()); ++i) {
    expect_close(actual[i], expected[i], tol, "linear response mismatch");
  }
  std::printf("linear_csr_eval ok\n");
  return 0;
}
'''
        output = compile_and_run_harness(
            self,
            source,
            ("src/linear_csr_eval.cu",),
        )
        self.assertIn("linear_csr_eval ok", output)


if __name__ == "__main__":
    unittest.main()
