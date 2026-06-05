import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARITY_DOC = ROOT / "docs" / "CUDA_OPERATOR_PARITY.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cuda_diff_utils import base_harness_prelude, compile_and_run_harness


class CUDAClauseEvalDifferentialTests(unittest.TestCase):
    def test_parity_doc_names_maxsat_clause_contract(self):
        text = PARITY_DOC.read_text(encoding="utf-8")

        self.assertIn("MaxSAT Clause Evaluation", text)
        self.assertIn("target_id: maxsat_clause_eval", text)
        self.assertIn("cuda/src/clause_eval.cu", text)
        self.assertIn("apc_eval_clause_csr", text)
        self.assertIn("apc.readings.maxsat.eval_unsatisfied_clauses", text)
        self.assertIn("unsatisfied_indicator: 0_or_1", text)
        self.assertIn("comparison: exact", text)
        self.assertNotIn("speedup", text.lower())

    def test_clause_eval_matches_cpu_unsatisfied_indicators(self):
        source = base_harness_prelude() + r'''
int main() {
  const int batch_size = 3;
  const int n_vars = 3;
  const int n_clauses = 3;

  std::vector<int32_t> clause_ptr = {0, 2, 4, 6};
  std::vector<int32_t> lit_var = {0, 1, 0, 2, 1, 2};
  std::vector<int8_t> lit_sign = {1, 1, -1, 1, -1, -1};
  std::vector<double> weight = {1.0, 2.0, 1.5};
  std::vector<int32_t> states = {
      0, 0, 0,
      1, 0, 1,
      0, 1, 1,
  };
  std::vector<int32_t> expected = {
      1, 0, 0,
      0, 0, 0,
      0, 0, 1,
  };

  int32_t* d_clause_ptr = device_copy(clause_ptr);
  int32_t* d_lit_var = device_copy(lit_var);
  int8_t* d_lit_sign = device_copy(lit_sign);
  double* d_weight = device_copy(weight);
  int32_t* d_states = device_copy(states);
  int32_t* d_unsatisfied = nullptr;
  require_cuda(cudaMalloc(&d_unsatisfied, sizeof(int32_t) * expected.size()), "unsatisfied malloc");

  APC_ClauseCSR clauses = {n_clauses, n_vars, static_cast<int32_t>(lit_var.size()), d_clause_ptr, d_lit_var, d_lit_sign, d_weight};
  APC_StateBatch state_batch = {batch_size, n_vars, d_states};
  APC_ClauseBatch output = {batch_size, n_clauses, d_unsatisfied, nullptr};

  require_status(apc_eval_clause_csr(&clauses, &state_batch, &output, nullptr), "clause eval failed");
  require_cuda(cudaDeviceSynchronize(), "sync");

  std::vector<int32_t> actual = host_copy(d_unsatisfied, static_cast<int>(expected.size()));
  for (int i = 0; i < static_cast<int>(expected.size()); ++i) {
    require_ok(actual[i] == expected[i], "clause eval mismatch");
  }
  std::printf("clause_eval ok\n");
  return 0;
}
'''
        output = compile_and_run_harness(
            self,
            source,
            ("src/clause_eval.cu",),
        )
        self.assertIn("clause_eval ok", output)


if __name__ == "__main__":
    unittest.main()
