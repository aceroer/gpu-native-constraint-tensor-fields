import unittest

from apc import (
    ReductionConfig,
    branch_tensor_from_state_pool,
    initialize_state_pool,
    load_problem_json,
    lower_problem_to_ctir,
    mask_branch_tensor,
    reduce_branch_tensor,
    reduction_gate_summary,
)


class ReductionGateTests(unittest.TestCase):
    def test_top_k_filtering_is_reproducible(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=3)
        pool = initialize_state_pool(ctir)
        tensor = branch_tensor_from_state_pool(ctir, pool)

        first = reduce_branch_tensor(ctir, pool, tensor, config=ReductionConfig(top_k=2))
        second = reduce_branch_tensor(ctir, pool, tensor, config=ReductionConfig(top_k=2))

        self.assertEqual(
            [(item.route.state_index, item.route.route_index) for item in first.selected],
            [(item.route.state_index, item.route.route_index) for item in second.selected],
        )
        self.assertEqual(len(first.selected), 2)

    def test_diversity_penalty_is_recorded_for_repeated_canonical_routes(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=2)
        pool = initialize_state_pool(ctir)
        tensor = branch_tensor_from_state_pool(ctir, pool)
        alive = ((True, False, False), (True, False, False))
        tensor = mask_branch_tensor(tensor, alive)

        result = reduce_branch_tensor(
            ctir,
            pool,
            tensor,
            config=ReductionConfig(top_k=2, diversity_weight=5.0),
        )

        self.assertEqual(len(result.selected), 2)
        self.assertEqual(result.selected[0].diversity_penalty, 0.0)
        self.assertEqual(result.selected[1].diversity_penalty, 5.0)

    def test_selected_actions_can_be_summarized_for_ledger(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=2)
        pool = initialize_state_pool(ctir)
        tensor = branch_tensor_from_state_pool(ctir, pool)

        result = reduce_branch_tensor(ctir, pool, tensor, config=ReductionConfig(top_k=1))
        summary = reduction_gate_summary(result)

        self.assertEqual(summary["top_k"], 1)
        self.assertEqual(summary["selected_count"], 1)
        self.assertIn("adjusted_energy", summary["selected"][0])
        self.assertIn("payload", summary["selected"][0])

    def test_masked_routes_are_not_selected(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=1)
        pool = initialize_state_pool(ctir)
        tensor = branch_tensor_from_state_pool(ctir, pool)
        tensor = mask_branch_tensor(tensor, ((False, True, False),))

        result = reduce_branch_tensor(ctir, pool, tensor, config=ReductionConfig(top_k=2))

        self.assertEqual(len(result.selected), 1)
        self.assertEqual(result.selected[0].route.route_index, 1)


if __name__ == "__main__":
    unittest.main()
