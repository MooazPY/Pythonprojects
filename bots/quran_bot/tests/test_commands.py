import unittest

from bot.commands.quran import QuranCommands


class DummyBot:
    def __init__(self):
        from bot.services.quran_api import QuranService

        self.config = type("C", (), {"daily_brand": "Daily Quran", "default_embed_color": "1E8DD3"})()
        self.store = type("S", (), {"get_guild_settings": lambda self, guild_id: {}})()
        self.quran_service = QuranService()


class QuranCommandsTests(unittest.TestCase):
    def test_build_ayah_embed(self):
        bot = DummyBot()
        commands = QuranCommands(bot)
        payload = {
            "surah": {"number": 1, "englishName": "Al-Fatihah"},
            "numberInSurah": 1,
            "text": "الحمد لله رب العالمين",
        }
        embed = commands._build_ayah_embed(payload, "All praise is due to Allah, Lord of the worlds.", "en", "Daily Quran", 0x1E8DD3)
        self.assertEqual(embed.title, "Daily Quran — Surah 1:1")
        self.assertTrue(embed.description.startswith("الحمد لله"))
        self.assertEqual(embed.fields[0].name, "Surah")
        self.assertEqual(embed.fields[1].name, "Ayah")
        self.assertEqual(embed.fields[2].name, "Translation (Sahih International)")


if __name__ == "__main__":
    unittest.main()
