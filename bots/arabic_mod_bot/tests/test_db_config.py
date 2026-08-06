"""Unit tests for SQLite ConfigStore."""

import asyncio
import os
import pytest
from config.db_config import ConfigStore, GuildConfig


def test_get_and_save_config(tmp_path):
    async def _run():
        db_file = os.path.join(tmp_path, "test_bot.db")
        store = ConfigStore(db_path=db_file)
        cfg = await store.get_config(guild_id=12345)
        assert cfg.guild_id == 12345
        assert cfg.ai_filter_enabled is True
        assert cfg.ai_confidence_threshold == 0.80

        cfg.ai_confidence_threshold = 0.85
        await store.save_config(cfg)

        await store.invalidate(12345)
        updated_cfg = await store.get_config(guild_id=12345)
        assert updated_cfg.ai_confidence_threshold == 0.85

    asyncio.run(_run())


def test_warnings_and_stats(tmp_path):
    async def _run():
        db_file = os.path.join(tmp_path, "test_bot.db")
        store = ConfigStore(db_path=db_file)
        guild_id = 999
        user_id = 456

        count1 = await store.add_warning(guild_id, user_id, "سبام", moderator_id=111)
        assert count1 == 1

        count2 = await store.add_warning(guild_id, user_id, "سلوك سيء", moderator_id=111)
        assert count2 == 2

        stored_count = await store.get_warning_count(guild_id, user_id)
        assert stored_count == 2

        await store.clear_warnings(guild_id, user_id)
        cleared_count = await store.get_warning_count(guild_id, user_id)
        assert cleared_count == 0

    asyncio.run(_run())
