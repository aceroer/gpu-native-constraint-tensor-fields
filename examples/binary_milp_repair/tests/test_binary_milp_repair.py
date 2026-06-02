import unittest

from apc_example import BinaryDomain, LinearCSR, RepairConfig, StateBatch
from apc_example.cpu_reference import (
    energy,
    eval_linear_response,
    positive_violation,
    weighted_penalty,
)
from apc_example.repair_loop import repair_binary_milp
from apc_example.validation import (
    assert_binary_domain,
    assert_linear_csr_sane,
    assert_nonnegative_violations,
)


def tiny_problem():
    # Constraints:
    # x0 + x1 >= 1
    # x1 + x2 >= 1
    # x0 + x2 <= 1
    linear = LinearCSR(
        n_rows=3,
        n_vars=3,
        row_ptr=(0, 2, 4, 6),
        col_idx=(0, 1, 1, 2, 0, 2),
        coeff=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
        rhs=(1.0, 1.0, 1.0),
        sense=(">=", ">=", "<="),
        weight=(1.0, 1.0, 1.0),
    )
    cost = (2.0, 1.0, 2.0)
    domain = BinaryDomain(n_vars=3)
    batch = StateBatch(((0, 0, 0), (1, 1, 1), (1, 0, 0), (0, 1, 0)))
    return domain, linear, cost, batch


class BinaryMilpRepairTests(unittest.TestCase):
    def test_response_violation_and_penalty(self):
        _, linear, _, batch = tiny_problem()
        response = eval_linear_response(batch, linear)
        violation = positive_violation(response, linear)
        penalty = weighted_penalty(violation, linear)

        self.assertEqual(response[0], [-1.0, -1.0, -1.0])
        self.assertEqual(violation[0], [1.0, 1.0, 0.0])
        self.assertEqual(penalty[0], 2.0)
        assert_nonnegative_violations(violation)

    def test_repair_finds_feasible_candidate(self):
        domain, linear, cost, batch = tiny_problem()
        assert_linear_csr_sane(linear)
        result = repair_binary_milp(
            domain,
            linear,
            cost,
            batch,
            RepairConfig(max_iters=8, lambda_penalty=10.0),
        )

        self.assertIsNotNone(result.best_state)
        self.assertEqual(result.best_penalty, 0.0)
        self.assertEqual(result.best_state, (0, 1, 0))
        self.assertEqual(result.best_objective, 1.0)
        assert_binary_domain(result.final_batch, domain)

    def test_energy_ledger_shapes(self):
        _, linear, cost, batch = tiny_problem()
        values, penalties, violations = energy(batch, linear, cost, 10.0, 1.0)
        self.assertEqual(len(values), batch.batch_size)
        self.assertEqual(len(penalties), batch.batch_size)
        self.assertEqual(len(violations), batch.batch_size)
        self.assertEqual(len(violations[0]), linear.n_rows)


if __name__ == "__main__":
    unittest.main()

