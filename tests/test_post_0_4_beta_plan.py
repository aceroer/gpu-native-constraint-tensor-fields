import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "POST_0_4_BETA_PLAN.md"
DEBUGGING = ROOT / "docs" / "DEBUGGING.md"
ROADMAP = ROOT / "ROADMAP.md"


class Post04BetaPlanTests(unittest.TestCase):
    def test_plan_names_tcc_compute_and_windows_orchestration_split(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("0.4 Beta Real-Environment Split", text)
        self.assertIn("TCC or headless CUDA compute core", text)
        self.assertIn("Windows orchestration layer", text)
        self.assertIn("core runtime first", text)
        self.assertIn("Windows orchestration second", text)
        self.assertIn("WDDM", text)

    def test_plan_names_pci_hal_cudaos_longer_target(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("PCI hardware contract", text)
        self.assertIn("GPU HAL", text)
        self.assertIn("CUDAOS-owned device control", text)
        self.assertIn("PCI/PCIe enumeration is the only CPU-side hardware contract", text)
        self.assertIn("PCI BAR-space", text)
        self.assertIn("not a claim that the current beta bypasses vendor", text)
        self.assertIn("OS security boundaries", text)
        self.assertIn("not purely commercial", text)
        self.assertIn("vendor and\ncustomer agreement first", text)
        self.assertIn("restricted closed-source hardware-control layer", text)
        self.assertIn("hardware-control layer", text)
        self.assertIn("public runtime", text)
        self.assertIn("remain useful", text)

    def test_plan_classifies_real_environment_failures(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("CUDA operator failures", text)
        self.assertIn("CUDA environment failures", text)
        self.assertIn("host compiler and build-tool failures", text)
        self.assertIn("shell, path, and packaging failures", text)
        self.assertIn("Missing TCC is recorded as an environment fact", text)

    def test_debugging_doc_records_beta_rule(self):
        text = DEBUGGING.read_text(encoding="utf-8")

        self.assertIn("Real-Environment Split", text)
        self.assertIn("TCC or headless CUDA lane", text)
        self.assertIn("Windows hosts should be treated as orchestration layers", text)
        self.assertIn("core runtime first", text)
        self.assertIn("Windows orchestration second", text)
        self.assertIn("PCI hardware contract", text)
        self.assertIn("GPU HAL", text)
        self.assertIn("CUDAOS-owned device control", text)
        self.assertIn("Register-level and PCI BAR-space facts", text)
        self.assertIn("vendor-agreed restricted hardware-control layer", text)
        self.assertIn("customer, GPU vendor, interface permissions", text)
        self.assertIn("open-source route should not depend on restricted control", text)

    def test_roadmap_points_to_0_4_beta_plan(self):
        text = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("docs/POST_0_4_BETA_PLAN.md", text)
        self.assertIn("0.4 beta real-environment split", text)
        self.assertIn("TCC or headless CUDA lane", text)
        self.assertIn("Windows as an orchestration layer", text)
        self.assertIn("PCI/PCIe is the hardware contract", text)
        self.assertIn("GPU HAL", text)
        self.assertIn("CUDAOS owns the", text)
        self.assertIn("vendor-agreed\nrestricted hardware-control layer", text)
        self.assertIn("customer, GPU vendor, interface\npermissions", text)


if __name__ == "__main__":
    unittest.main()
