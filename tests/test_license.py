import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LicenseTests(unittest.TestCase):
    def test_license_file_is_mit(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")

        self.assertIn("MIT License", text)
        self.assertIn("Permission is hereby granted, free of charge", text)
        self.assertIn("aceroer", text)

    def test_pyproject_license_matches_file(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn('license = { text = "MIT" }', text)

    def test_notice_records_original_source(self):
        text = (ROOT / "NOTICE").read_text(encoding="utf-8")

        self.assertIn("GPU-Native Constraint Tensor Fields", text)
        self.assertIn("Original author: aceroer", text)
        self.assertIn("https://github.com/aceroer/gpu-native-constraint-tensor-fields", text)
        self.assertIn("Recommended attribution", text)

    def test_citation_metadata_names_repository(self):
        text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")

        self.assertIn("cff-version: 1.2.0", text)
        self.assertIn('alias: "aceroer"', text)
        self.assertIn('license: "MIT"', text)
        self.assertIn("repository-code: \"https://github.com/aceroer/gpu-native-constraint-tensor-fields\"", text)

    def test_origin_doc_records_public_lineage(self):
        text = (ROOT / "docs" / "ORIGIN.md").read_text(encoding="utf-8")

        self.assertIn("Original author: aceroer", text)
        self.assertIn("First public source date: 2026-06-02", text)
        self.assertIn("StatePool", text)
        self.assertIn("release verifier", text)


if __name__ == "__main__":
    unittest.main()
