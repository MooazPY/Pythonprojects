"""Unit tests for SQLite ConfigStore."""

import asyncio
import os
import tempfile
from config.db_config import ConfigStore, GuildConfig


def test_get_and_save_config():
    async def _run():
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = os.path.join(tmp_dir, "test_bot.db")
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


def test_warnings_and_stats():
    async def _run():
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = os.path.join(tmp_dir, "test_bot.db")
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


def test_whitelisted_domains_add_and_remove():
    async def _run():
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = os.path.join(tmp_dir, "test_bot.db")
            store = ConfigStore(db_path=db_file)
            guild_id = 777

            await store.add_whitelisted_domain(guild_id, "example.com")
            cfg = await store.get_config(guild_id)
            assert "example.com" in cfg.whitelisted_domains

            await store.remove_whitelisted_domain(guild_id, "example.com")
            await store.invalidate(guild_id)
            updated_cfg = await store.get_config(guild_id)
            assert "example.com" not in updated_cfg.whitelisted_domains

    asyncio.run(_run())


def test_decrement_warning():
    async def _run():
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = os.path.join(tmp_dir, "test_bot.db")
            store = ConfigStore(db_path=db_file)
            guild_id = 888
            user_id = 333

            await store.add_warning(guild_id, user_id, "W1", 1)
            await store.add_warning(guild_id, user_id, "W2", 1)
            assert await store.get_warning_count(guild_id, user_id) == 2

            new_count = await store.decrement_warning(guild_id, user_id, 1)
            assert new_count == 1
            assert await store.get_warning_count(guild_id, user_id) == 1

    asyncio.run(_run())



