import unittest

from apc import (
    StateBatch,
    initialize_state_pool,
    load_problem_json,
    lower_problem_to_ctir,
    mask_state_pool,
    state_pool_summary,
    state_pool_with_scores,
)
from apc.state_pool import StatePool


class StatePoolTests(unittest.TestCase):
    def test_initialize_state_pool_from_ctir(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=4)

        pool = initialize_state_pool(ctir)

        self.assertEqual(pool.batch_size, 4)
        self.assertEqual(pool.n_vars, 3)
        self.assertEqual(pool.states.x[0], (0, 0, 0))
        self.assertEqual(pool.alive_count, 4)
        self.assertEqual(pool.metadata[0]["origin"], "ctir_init")

    def test_state_pool_records_scores_and_alive_mask(self):
        states = StateBatch(((0, 0), (1, 0), (1, 1)))
        pool = StatePool(
            states=states,
            scores=(0.0, 0.0, 0.0),
            uncertainty=(1.0, 1.0, 1.0),
            alive_mask=(True, True, True),
            metadata=({}, {}, {}),
        )

        scored = state_pool_with_scores(pool, (3.0, 1.0, 2.0))
        masked = mask_state_pool(scored, (False, True, True))

        self.assertEqual(masked.scores, (3.0, 1.0, 2.0))
        self.assertEqual(masked.alive_count, 2)

    def test_state_pool_summary_is_json_ready(self):
        spec = load_problem_json("examples/specs/binary_milp_tiny.json")
        ctir = lower_problem_to_ctir(spec, batch_size=2)
        pool = initialize_state_pool(ctir)

        summary = state_pool_summary(pool)

        self.assertEqual(summary["batch_size"], 2)
        self.assertEqual(summary["n_vars"], 3)
        self.assertEqual(summary["alive_count"], 2)
        self.assertEqual(summary["alive_mask"], [True, True])
        self.assertEqual(summary["metadata"][0]["origin"], "ctir_init")

    def test_state_pool_validates_annotation_lengths(self):
        states = StateBatch(((0, 0), (1, 1)))

        with self.assertRaisesRegex(ValueError, "scores length"):
            StatePool(
                states=states,
                scores=(0.0,),
                uncertainty=(1.0, 1.0),
                alive_mask=(True, True),
                metadata=({}, {}),
            )


if __name__ == "__main__":
    unittest.main()
