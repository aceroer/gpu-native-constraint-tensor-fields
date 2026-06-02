import tempfile
import unittest
from pathlib import Path

from apc import load_problem_json, problem_to_json_dict, save_problem_json
from apc.io_json import problem_from_json_dict


ROOT = Path(__file__).resolve().parents[1]
TINY_SPEC = ROOT / "examples" / "specs" / "binary_milp_tiny.json"


class SpecLoadingTests(unittest.TestCase):
    def test_load_tiny_spec(self):
        problem = load_problem_json(TINY_SPEC)

        self.assertEqual(problem.domain.n_vars, 3)
        self.assertEqual(problem.objective.linear, (2.0, 1.0, 2.0))
        self.assertEqual(problem.linear_csr.n_rows, 3)
        self.assertEqual(problem.linear_csr.row_ptr, (0, 2, 4, 6))
        self.assertEqual(problem.linear_csr.sense, (">=", ">=", "<="))

    def test_reject_malformed_csr(self):
        data = problem_to_json_dict(load_problem_json(TINY_SPEC))
        data["constraints"]["linear_csr"]["row_ptr"] = [0, 2, 4]

        with self.assertRaisesRegex(ValueError, "row_ptr length"):
            problem_from_json_dict(data)

    def test_reject_unsupported_domain(self):
        data = problem_to_json_dict(load_problem_json(TINY_SPEC))
        data["domain"]["type"] = "integer"

        with self.assertRaisesRegex(ValueError, "only binary domains"):
            problem_from_json_dict(data)

    def test_reject_unsupported_row_sense(self):
        data = problem_to_json_dict(load_problem_json(TINY_SPEC))
        data["constraints"]["linear_csr"]["sense"] = [">=", "!=", "<="]

        with self.assertRaisesRegex(ValueError, "unsupported row sense"):
            problem_from_json_dict(data)

    def test_round_trip_tiny_spec(self):
        problem = load_problem_json(TINY_SPEC)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "round_trip.json"
            save_problem_json(problem, path)
            round_trip = load_problem_json(path)

        self.assertEqual(problem, round_trip)


if __name__ == "__main__":
    unittest.main()

