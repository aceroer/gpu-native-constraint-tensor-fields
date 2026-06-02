import json
import tempfile
import unittest
from pathlib import Path

from apc.benchmark_sweep import (
    TIMING_FIELDS,
    BenchmarkSweepCase,
    BenchmarkSweepConfig,
    benchmark_sweep_config_from_dict,
    benchmark_sweep_config_to_dict,
    load_benchmark_sweep_config,
    write_benchmark_sweep_config,
)


ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "benchmarks" / "sweeps" / "binary_milp_smoke.json"


class BenchmarkSweepConfigTests(unittest.TestCase):
    def test_sweep_config_is_json_ready(self):
        config = BenchmarkSweepConfig(
            name="smoke",
            cases=(
                BenchmarkSweepCase(
                    name="cpu_case",
                    spec="examples/specs/binary_milp_tiny.json",
                    backend="cpu",
                    out="benchmarks/sweeps/out/cpu.json",
                    max_iters=2,
                ),
            ),
        )
        payload = benchmark_sweep_config_to_dict(config)

        encoded = json.dumps(payload, sort_keys=True)

        self.assertEqual(payload["schema"], "apc.benchmark_sweep_config.v1")
        self.assertIn("cpu_case", encoded)
        self.assertEqual(payload["timing_fields"], list(TIMING_FIELDS))

    def test_example_sweep_config_loads_and_names_required_fields(self):
        config = load_benchmark_sweep_config(SWEEP)

        self.assertEqual(config.name, "binary_milp_smoke")
        self.assertEqual(len(config.cases), 2)
        for case in config.cases:
            with self.subTest(case=case.name):
                self.assertTrue(case.spec.endswith(".json"))
                self.assertIn(case.backend, {"cpu", "cuda"})
                self.assertGreaterEqual(case.max_iters, 0)
                self.assertTrue(case.out.startswith("benchmarks/sweeps/out/"))

    def test_sweep_config_round_trips(self):
        config = load_benchmark_sweep_config(SWEEP)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "sweep.json"
            write_benchmark_sweep_config(config, out)
            loaded = load_benchmark_sweep_config(out)

        self.assertEqual(loaded, config)

    def test_sweep_config_rejects_invalid_cases(self):
        with self.assertRaises(ValueError):
            BenchmarkSweepCase(
                name="bad_backend",
                spec="examples/specs/binary_milp_tiny.json",
                backend="gpu",
                out="benchmarks/sweeps/out/bad.json",
            )
        with self.assertRaises(ValueError):
            BenchmarkSweepCase(
                name="bad_iters",
                spec="examples/specs/binary_milp_tiny.json",
                backend="cpu",
                out="benchmarks/sweeps/out/bad.json",
                max_iters=-1,
            )

    def test_sweep_config_rejects_duplicate_case_names(self):
        case = BenchmarkSweepCase(
            name="same",
            spec="examples/specs/binary_milp_tiny.json",
            backend="cpu",
            out="benchmarks/sweeps/out/a.json",
        )

        with self.assertRaises(ValueError):
            BenchmarkSweepConfig(name="bad", cases=(case, case))

    def test_sweep_config_rejects_missing_timing_fields(self):
        case = BenchmarkSweepCase(
            name="case",
            spec="examples/specs/binary_milp_tiny.json",
            backend="cpu",
            out="benchmarks/sweeps/out/a.json",
        )

        with self.assertRaises(ValueError):
            BenchmarkSweepConfig(
                name="bad",
                cases=(case,),
                timing_fields=("kernel_time_s",),
            )

    def test_sweep_config_parser_rejects_wrong_schema(self):
        with self.assertRaises(ValueError):
            benchmark_sweep_config_from_dict({"schema": "wrong", "name": "bad", "cases": []})

    def test_sweep_docs_keep_timing_and_no_claim_boundary(self):
        text = (ROOT / "docs" / "BENCHMARK_SWEEPS.md").read_text(encoding="utf-8")

        for field in TIMING_FIELDS:
            self.assertIn(field, text)
        self.assertIn("apc.benchmark_sweep_config.v1", text)
        self.assertIn("benchmarks/sweeps/binary_milp_smoke.json", text)
        self.assertNotIn("speedup", text.lower())


if __name__ == "__main__":
    unittest.main()
