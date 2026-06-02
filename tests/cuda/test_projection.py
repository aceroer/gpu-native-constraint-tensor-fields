import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARITY_DOC = ROOT / "docs" / "CUDA_OPERATOR_PARITY.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cuda_diff_utils import base_harness_prelude, compile_and_run_harness


class CUDAProjectionDifferentialTests(unittest.TestCase):
    def test_parity_doc_names_projection_contract(self):
        text = PARITY_DOC.read_text(encoding="utf-8")

        self.assertIn("cuda/src/projection.cu", text)
        self.assertIn("apc_project_binary", text)
        self.assertIn("apc.operators_cpu.apply_projection", text)
        self.assertIn("projected_values: 0_or_1", text)
        self.assertIn("projection_rule: x >= 1 -> 1, otherwise 0", text)
        self.assertIn("kernel_time_s", text)
        self.assertIn("copy_time_s", text)
        self.assertIn("layout_conversion_time_s", text)
        self.assertIn("end_to_end_time_s", text)
        self.assertNotIn("speedup", text.lower())

    def test_projection_keeps_binary_domain(self):
        source = base_harness_prelude() + r'''
int main() {
  const int batch_size = 3;
  const int n_vars = 5;
  std::vector<int32_t> states = {
      -2, 0, 1, 3, -1,
      2, 2, 0, -3, 1,
      0, -1, 7, 1, 4,
  };
  std::vector<int32_t> expected(states.size(), 0);
  for (int i = 0; i < static_cast<int>(states.size()); ++i) {
    expected[i] = states[i] >= 1 ? 1 : 0;
  }

  int32_t* d_states = device_copy(states);
  APC_StateBatch state_batch = {batch_size, n_vars, d_states};
  APC_RuntimeCtx ctx = {nullptr, &state_batch, nullptr, nullptr, nullptr, nullptr};

  require_status(apc_project_binary(&ctx), "projection failed");
  require_cuda(cudaDeviceSynchronize(), "sync");

  std::vector<int32_t> actual = host_copy(d_states, static_cast<int>(states.size()));
  for (int i = 0; i < static_cast<int>(states.size()); ++i) {
    require_ok(actual[i] == 0 || actual[i] == 1, "projected value outside binary domain");
    require_ok(actual[i] == expected[i], "projection mismatch");
  }
  std::printf("projection ok\n");
  return 0;
}
'''
        output = compile_and_run_harness(
            self,
            source,
            ("src/projection.cu",),
        )
        self.assertIn("projection ok", output)


if __name__ == "__main__":
    unittest.main()
