import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LicenseTests(unittest.TestCase):
    def test_license_file_is_mit(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")

        self.assertIn("MIT License", text)
        self.assertIn("Permission is hereby granted, free of charge", text)
        self.assertIn("APC contributors", text)

    def test_pyproject_license_matches_file(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn('license = { text = "MIT" }', text)


if __name__ == "__main__":
    unittest.main()
