import unittest

from apc import LinearCSR, StateBatch
from apc.layout_materialize import (
    ActiveViolationCompact,
    LinearCSC,
    materialize_active_violations,
    materialize_linear_csc,
    materialize_variable_major,
)


class LayoutMaterializeTests(unittest.TestCase):
    def test_candidate_major_to_variable_major_is_deterministic(self):
        states = StateBatch(((0, 1, 0), (1, 0, 1), (1, 1, 0)))
        materialized = materialize_variable_major(states)

        self.assertEqual(materialized.data, ((0, 1, 1), (1, 0, 1), (0, 1, 0)))
        self.assertEqual(materialized.cost.elements_read, 9)
        self.assertEqual(materialized.cost.elements_written, 9)

    def test_csr_to_csc_preserves_nonzeros(self):
        linear = LinearCSR(
            n_rows=3,
            n_vars=3,
            row_ptr=(0, 2, 4, 6),
            col_idx=(0, 1, 1, 2, 0, 2),
            coeff=(1.0, 2.0, 3.0, 4.0, 5.0, 6.0),
            rhs=(1.0, 1.0, 1.0),
            sense=(">=", ">=", "<="),
            weight=(1.0, 1.0, 1.0),
        )
        materialized = materialize_linear_csc(linear)
        csc = materialized.data

        self.assertIsInstance(csc, LinearCSC)
        self.assertEqual(csc.col_ptr, (0, 2, 4, 6))
        self.assertEqual(csc.row_idx, (0, 2, 0, 1, 1, 2))
        self.assertEqual(csc.coeff, (1.0, 5.0, 2.0, 3.0, 4.0, 6.0))
        self.assertEqual(csc.nnz, linear.nnz)
        self.assertEqual(materialized.cost.elements_read, 6)
        self.assertEqual(materialized.cost.elements_written, 6)

    def test_active_violation_compaction_records_cost(self):
        violations = ((0.0, 1.5, 0.0), (2.0, 0.0, 3.0))
        materialized = materialize_active_violations(violations)
        compact = materialized.data

        self.assertIsInstance(compact, ActiveViolationCompact)
        self.assertEqual(compact.entries, ((0, 1, 1.5), (1, 0, 2.0), (1, 2, 3.0)))
        self.assertEqual(materialized.cost.elements_read, 6)
        self.assertEqual(materialized.cost.elements_written, 3)


if __name__ == "__main__":
    unittest.main()
