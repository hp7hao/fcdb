import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_promotion.py")


class CheckPromotionTests(unittest.TestCase):
    def run_gate(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_allows_current_stable_schema(self) -> None:
        result = self.run_gate(
            "--platform", "pico8",
            "--candidate-schema", "0.4.0",
            "--stable-contract", "0.4.0",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Stable promotion allowed", result.stdout)

    def test_blocks_breaking_candidate_from_legacy_channel(self) -> None:
        result = self.run_gate(
            "--platform", "pico8",
            "--candidate-schema", "0.5.0",
            "--stable-contract", "legacy-1.0",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("each downstream consumer's own full FCDB package suite", result.stderr)
        self.assertIn("release owner authorizes cutover", result.stderr)
        self.assertIn("checked-in stable schema version", result.stderr)

    def test_allows_breaking_candidate_without_stable_promotion(self) -> None:
        result = self.run_gate(
            "--platform", "pyxel",
            "--candidate-schema", "0.5.0",
            "--stable-contract", "legacy-1.0",
            "--candidate-only",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Candidate-only publication allowed", result.stdout)
        self.assertIn("pyxel-latest remains contract legacy-1.0", result.stdout)

    def test_rejects_non_semver_candidate_schema(self) -> None:
        result = self.run_gate(
            "--platform", "pyxelpico",
            "--candidate-schema", "latest",
            "--stable-contract", "legacy-1.0",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Semantic Versioning", result.stderr)


if __name__ == "__main__":
    unittest.main()
