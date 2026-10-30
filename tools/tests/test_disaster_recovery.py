import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from postgres_backup import backup_name, postgres_environment
from postgres_restore import assert_disposable_database


class DisasterRecoveryTests(unittest.TestCase):
    def test_connection_is_passed_by_environment_not_command_line(self):
        env, database = postgres_environment("postgresql://user:secret@example.invalid:5432/judicial3_staging")
        self.assertEqual(database, "judicial3_staging")
        self.assertEqual(env["PGPASSWORD"], "secret")
        self.assertEqual(env["PGSSLMODE"], "require")

    def test_backup_names_are_unique_timestamped_and_encrypted(self):
        name = backup_name("judicial3_staging", datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(name, "judicial3-judicial3_staging-20261030T120000Z.dump.age")

    def test_restore_refuses_non_disposable_database(self):
        with self.assertRaises(RuntimeError):
            assert_disposable_database("judicial3")
        assert_disposable_database("judicial3_restore")


if __name__ == "__main__":
    unittest.main()
