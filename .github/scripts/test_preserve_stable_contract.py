import unittest

from preserve_stable_contract import contract_identity


class ContractIdentityTests(unittest.TestCase):
    def test_reads_schema_manifest(self) -> None:
        self.assertEqual(contract_identity({"schema_version": "0.5.0"}), ("0.5.0", "schema"))

    def test_reads_public_legacy_manifest(self) -> None:
        self.assertEqual(contract_identity({"version": "1.0"}), ("legacy-1.0", "contract"))

    def test_prefers_schema_over_legacy_version(self) -> None:
        self.assertEqual(
            contract_identity({"schema_version": "0.5.0", "version": "1.0"}),
            ("0.5.0", "schema"),
        )

    def test_rejects_missing_contract_identity(self) -> None:
        with self.assertRaisesRegex(ValueError, "neither schema_version"):
            contract_identity({"platform": "pico8"})


if __name__ == "__main__":
    unittest.main()
