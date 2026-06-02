import unittest

from apc import (
    branch_tensor_from_state_pool,
    branch_tensor_summary,
    canonical_branch_keys,
    initialize_state_pool,
    load_problem_json,
    lower_problem_to_ctir,
    mask_branch_tensor,
    mask_state_pool,
)
from apc.branch_tensor import BranchTensor


class BranchTensorTests(unittest.TestCase):
    def test_branch_tensor_from_state_pool_has_explicit_shape(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=3)
        pool = initialize_state_pool(ctir)

        tensor = branch_tensor_from_state_pool(ctir, pool)

        self.assertEqual(tensor.shape, (3, 3))
        self.assertEqual(tensor.alive_count, 9)
        self.assertEqual(tensor.routes[0][0].move_type, "bit_flip")
        self.assertEqual(tensor.routes[0][0].payload, (0,))

    def test_canonical_branch_keys_ignore_state_index(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=2)
        pool = initialize_state_pool(ctir)
        tensor = branch_tensor_from_state_pool(ctir, pool)

        keys = canonical_branch_keys(tensor)

        self.assertEqual(keys[0], keys[1])
        self.assertEqual(keys[0], (("bit_flip", (0,)), ("bit_flip", (1,)), ("bit_flip", (2,))))

    def test_low_priority_branches_can_be_masked_without_changing_shape(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=2)
        pool = mask_state_pool(initialize_state_pool(ctir), (True, False))
        tensor = branch_tensor_from_state_pool(ctir, pool)

        masked = mask_branch_tensor(tensor, ((True, False, True), (False, False, False)))

        self.assertEqual(masked.shape, tensor.shape)
        self.assertEqual(masked.alive_count, 2)

    def test_branch_tensor_summary_is_json_ready(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=1)
        pool = initialize_state_pool(ctir)
        tensor = branch_tensor_from_state_pool(ctir, pool)

        summary = branch_tensor_summary(tensor)

        self.assertEqual(summary["shape"], [1, 3])
        self.assertEqual(summary["alive_count"], 3)
        self.assertEqual(summary["routes"][0][1]["canonical_key"], ["bit_flip", [1]])

    def test_branch_tensor_validates_fixed_width(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=2)
        pool = initialize_state_pool(ctir)
        tensor = branch_tensor_from_state_pool(ctir, pool)

        with self.assertRaisesRegex(ValueError, "fixed width"):
            BranchTensor(
                routes=(tensor.routes[0], tensor.routes[1][:-1]),
                alive_mask=(tensor.alive_mask[0], tensor.alive_mask[1][:-1]),
                metadata=(tensor.metadata[0], tensor.metadata[1][:-1]),
            )


if __name__ == "__main__":
    unittest.main()
