"""Unit tests for GuildConfig JSON export/import and Web Dashboard API."""

import asyncio
import json
import os
import tempfile
from unittest.mock import MagicMock
from config.db_config import ConfigStore, GuildConfig
from web_dashboard import WebDashboardServer


def test_guild_config_to_dict_and_from_dict():
    cfg = GuildConfig(guild_id=123, warn_threshold_mute=5, custom_bad_words=["كلمة1", "كلمة2"])
    d = cfg.to_dict()

    assert d["warn_threshold_mute"] == 5
    assert d["custom_bad_words"] == ["كلمة1", "كلمة2"]

    restored = GuildConfig.from_dict(123, d)
    assert restored.guild_id == 123
    assert restored.warn_threshold_mute == 5
    assert restored.custom_bad_words == ["كلمة1", "كلمة2"]


def test_config_import_json_applied(tmp_path):
    async def _run():
        db_file = os.path.join(tmp_path, "test_bot.db")
        store = ConfigStore(db_path=db_file)
        guild_id = 555

        # Create original config
        orig = await store.get_config(guild_id)
        assert orig.warn_threshold_mute == 3

        # Simulated imported JSON payload
        imported_payload = {
            "warn_threshold_mute": 7,
            "ai_confidence_threshold": 0.92,
            "custom_bad_words": ["سبام_مخصص"],
            "whitelisted_domains": ["trusted.com"],
        }

        # Apply import logic
        cfg = await store.get_config(guild_id, use_cache=False)
        for k, v in imported_payload.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)

        await store.save_config(cfg)

        # Verify persisted changes
        await store.invalidate(guild_id)
        updated = await store.get_config(guild_id)
        assert updated.warn_threshold_mute == 7
        assert updated.ai_confidence_threshold == 0.92
        assert "سبام_مخصص" in updated.custom_bad_words
        assert "trusted.com" in updated.whitelisted_domains

    asyncio.run(_run())


def test_web_dashboard_stats_endpoint():
    async def _run():
        bot = MagicMock()
        bot.is_ready.return_value = True
        bot.guilds = []
        bot.user = "HarisBot#0001"

        server = WebDashboardServer(bot, port=9999)
        request = MagicMock()

        resp = await server.handle_api_stats(request)
        assert resp.status == 200
        body = json.loads(resp.body.decode("utf-8"))
        assert body["status"] == "online"
        assert body["bot_name"] == "HarisBot#0001"
        assert "stats_deleted_messages" in body

    asyncio.run(_run())

