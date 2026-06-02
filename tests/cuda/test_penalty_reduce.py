import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from cuda_diff_utils import base_harness_prelude, compile_and_run_harness


class CUDAPenaltyReduceDifferentialTests(unittest.TestCase):
    def test_violation_and_penalty_match_cpu_reference(self):
        source = base_harness_prelude() + r'''
int main() {
  const int batch_size = 3;
  const int n_vars = 4;
  const int n_rows = 4;
  const double tol = 1e-9;

  std::vector<int32_t> row_ptr = {0, 1, 2, 3, 4};
  std::vector<int32_t> col_idx = {0, 1, 2, 3};
  std::vector<double> coeff = {1.0, 1.0, 1.0, 1.0};
  std::vector<double> rhs = {1.0, 0.5, 2.0, -1.0};
  std::vector<int8_t> sense = {APC_SENSE_GE, APC_SENSE_LE, APC_SENSE_EQ, APC_SENSE_GE};
  std::vector<double> weight = {1.0, 2.0, 0.5, 1.5};
  std::vector<double> response = {
      0.0, 0.75, 2.25, -2.0,
      1.0, 0.25, 1.0, -1.0,
      2.0, 1.5, 2.0, 0.0,
  };
  std::vector<double> expected_violation(batch_size * n_rows, 0.0);
  std::vector<double> expected_penalty(batch_size, 0.0);
  for (int b = 0; b < batch_size; ++b) {
    for (int r = 0; r < n_rows; ++r) {
      double value = response[b * n_rows + r];
      double v = 0.0;
      if (sense[r] == APC_SENSE_LE) {
        v = std::fmax(value - rhs[r], 0.0);
      } else if (sense[r] == APC_SENSE_GE) {
        v = std::fmax(rhs[r] - value, 0.0);
      } else {
        v = std::fabs(value - rhs[r]);
      }
      expected_violation[b * n_rows + r] = v;
      expected_penalty[b] += weight[r] * v;
    }
  }

  int32_t* d_row_ptr = device_copy(row_ptr);
  int32_t* d_col_idx = device_copy(col_idx);
  double* d_coeff = device_copy(coeff);
  double* d_rhs = device_copy(rhs);
  int8_t* d_sense = device_copy(sense);
  double* d_weight = device_copy(weight);
  double* d_response = device_copy(response);
  double* d_violation = nullptr;
  double* d_penalty = nullptr;
  require_cuda(cudaMalloc(&d_violation, sizeof(double) * expected_violation.size()), "violation malloc");
  require_cuda(cudaMalloc(&d_penalty, sizeof(double) * expected_penalty.size()), "penalty malloc");

  APC_LinearCSR linear = {n_rows, n_vars, static_cast<int32_t>(col_idx.size()), d_row_ptr, d_col_idx, d_coeff, d_rhs, d_sense, d_weight};
  APC_ViolationBatch violations = {batch_size, n_rows, d_response, d_violation, d_penalty};
  APC_RuntimeCtx ctx = {&linear, nullptr, &violations, nullptr, nullptr, nullptr};

  require_status(apc_rectify_linear_violation(&ctx), "rectify failed");
  require_status(apc_reduce_weighted_penalty(&ctx), "penalty failed");
  require_cuda(cudaDeviceSynchronize(), "sync");

  std::vector<double> actual_violation = host_copy(d_violation, static_cast<int>(expected_violation.size()));
  std::vector<double> actual_penalty = host_copy(d_penalty, static_cast<int>(expected_penalty.size()));
  for (int i = 0; i < static_cast<int>(expected_violation.size()); ++i) {
    require_ok(actual_violation[i] >= 0.0, "negative violation");
    expect_close(actual_violation[i], expected_violation[i], tol, "violation mismatch");
  }
  for (int i = 0; i < batch_size; ++i) {
    expect_close(actual_penalty[i], expected_penalty[i], tol, "penalty mismatch");
  }
  std::printf("penalty_reduce ok\n");
  return 0;
}
'''
        output = compile_and_run_harness(
            self,
            source,
            ("src/violation_reduce.cu",),
        )
        self.assertIn("penalty_reduce ok", output)


if __name__ == "__main__":
    unittest.main()
