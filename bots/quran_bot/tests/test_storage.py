import unittest
from pathlib import Path

from bot.services.storage import GuildSettingsStore


class GuildSettingsStoreTests(unittest.TestCase):
    def test_persist_and_load_settings(self):
        db_path = Path(__file__).resolve().parent / "test_settings.sqlite3"
        store = GuildSettingsStore(str(db_path))
        try:
            store.save_guild_settings("123", {"channel_id": "456", "time": "08:00", "timezone": "UTC", "language": "en"})
            loaded = store.get_guild_settings("123")
            self.assertEqual(loaded["channel_id"], "456")
            self.assertEqual(loaded["time"], "08:00")
            self.assertEqual(loaded["timezone"], "UTC")
            self.assertEqual(loaded["language"], "en")
        finally:
            store.close()
            db_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
