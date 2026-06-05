import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARITY_DOC = ROOT / "docs" / "CUDA_OPERATOR_PARITY.md"


class CUDAParityTargetSelectionTests(unittest.TestCase):
    def test_phase_63_selects_qubo_and_maxsat_targets(self):
        text = PARITY_DOC.read_text(encoding="utf-8")

        self.assertIn("0.3 CUDA Parity Target Selection", text)
        self.assertIn("target_id: qubo_energy_eval", text)
        self.assertIn("cpu_reference: apc.runtime_qubo_cpu.eval_qubo_energy", text)
        self.assertIn("cuda_symbol: apc_eval_qubo_energy", text)
        self.assertIn("planned_phase: Phase 64", text)
        self.assertIn("target_id: qubo_bitflip_score", text)
        self.assertIn("cpu_reference: apc.runtime_qubo_cpu.score_qubo_bitflip_moves", text)
        self.assertIn("cuda_symbol: apc_score_qubo_bitflip_moves", text)
        self.assertIn("implemented_phase: Phase 70", text)
        self.assertIn("target_id: maxsat_clause_eval", text)
        self.assertIn("cpu_reference: apc.readings.maxsat.eval_unsatisfied_clauses", text)
        self.assertIn("cuda_symbol: apc_eval_clause_csr", text)

    def test_phase_63_keeps_cuda_selection_gated(self):
        text = PARITY_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("cpu reference route exists before cuda parity", text)
        self.assertIn("cuda tests skip cleanly", text)
        self.assertIn("no acceleration claim", text)
        self.assertNotIn("speedup", text)
        self.assertNotIn("drop-in solver", text)
        self.assertNotIn("solver-compatible", text)


if __name__ == "__main__":
    unittest.main()
