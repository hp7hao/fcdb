import unittest

from preserve_stable_contract import schema_identity


class SchemaIdentityTests(unittest.TestCase):
    def test_reads_schema_manifest(self) -> None:
        self.assertEqual(schema_identity({"schema_version": "0.5.0"}), "0.5.0")

    def test_marks_old_package_version_as_unversioned(self) -> None:
        self.assertEqual(schema_identity({"version": "1.0"}), "unversioned")

    def test_prefers_schema_over_old_package_version(self) -> None:
        self.assertEqual(
            schema_identity({"schema_version": "0.5.0", "version": "1.0"}),
            "0.5.0",
        )

    def test_marks_missing_schema_as_unversioned(self) -> None:
        self.assertEqual(schema_identity({"platform": "pico8"}), "unversioned")


if __name__ == "__main__":
    unittest.main()
