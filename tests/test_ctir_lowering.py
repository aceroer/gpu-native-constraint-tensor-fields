import json
import unittest
from pathlib import Path

from apc import (
    LinearCSR,
    ctir_json,
    ctir_to_dict,
    inspect_ctir,
    load_problem_json,
    lower_problem_to_ctir,
)


ROOT = Path(__file__).resolve().parents[1]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"


class CTIRLoweringTests(unittest.TestCase):
    def test_problem_spec_lowers_into_ctir(self):
        problem = load_problem_json(TINY_SPEC)
        ctir = lower_problem_to_ctir(problem, batch_size=8)

        self.assertEqual(ctir.domain.n_vars, 3)
        self.assertEqual(ctir.domain.var_type, ("binary", "binary", "binary"))
        self.assertIsNotNone(ctir.linear_csr)
        self.assertEqual(ctir.linear_csr.n_rows, 3)
        self.assertEqual(ctir.moves.move_type, "bit_flip")
        self.assertEqual(ctir.moves.batch_size, 8)
        self.assertEqual(ctir.projection.rules, ("binary",))

    def test_ctir_serializes_for_inspection(self):
        problem = load_problem_json(TINY_SPEC)
        ctir = lower_problem_to_ctir(problem)
        full = ctir_to_dict(ctir)
        compact = inspect_ctir(ctir)
        encoded = json.loads(ctir_json(ctir))

        self.assertEqual(full["linear_csr"]["nnz"], 6)
        self.assertEqual(compact["constraints"]["linear_rows"], 3)
        self.assertEqual(compact["moves"]["type"], "bit_flip")
        self.assertEqual(encoded["projection"]["rules"], ["binary"])

    def test_ctir_validation_catches_shape_errors(self):
        with self.assertRaisesRegex(ValueError, "row_ptr length"):
            LinearCSR(
                n_rows=3,
                n_vars=3,
                row_ptr=(0, 2, 4),
                col_idx=(0, 1, 1, 2),
                coeff=(1.0, 1.0, 1.0, 1.0),
                rhs=(1.0, 1.0, 1.0),
                sense=(">=", ">=", "<="),
                weight=(1.0, 1.0, 1.0),
            )

    def test_ctir_validation_catches_index_errors(self):
        with self.assertRaisesRegex(ValueError, "out of range"):
            LinearCSR(
                n_rows=1,
                n_vars=3,
                row_ptr=(0, 1),
                col_idx=(3,),
                coeff=(1.0,),
                rhs=(1.0,),
                sense=(">=",),
                weight=(1.0,),
            )

    def test_existing_example_uses_public_ctir(self):
        from apc.ctir import LinearCSR as PublicLinearCSR
        from apc.ctir import StateBatch as PublicStateBatch
        from apc_example.ctir import LinearCSR as ExampleLinearCSR
        from apc_example.ctir import StateBatch as ExampleStateBatch

        self.assertIs(ExampleLinearCSR, PublicLinearCSR)
        self.assertIs(ExampleStateBatch, PublicStateBatch)


if __name__ == "__main__":
    unittest.main()

