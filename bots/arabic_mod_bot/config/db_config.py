from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from config.auto_mod import PRESETS, apply_preset

DEFAULT_WARN_THRESHOLD = 3
DEFAULT_MUTE_MINUTES = 30
DEFAULT_AI_CONFIDENCE = 0.80


@dataclass
class GuildConfig:
    guild_id: int
    log_channel_id: Optional[int] = None
    mute_role_id: Optional[int] = None
    warn_threshold_mute: int = DEFAULT_WARN_THRESHOLD
    mute_duration_minutes: int = DEFAULT_MUTE_MINUTES
    profanity_filter_enabled: bool = True
    ai_filter_enabled: bool = True
    ai_confidence_threshold: float = DEFAULT_AI_CONFIDENCE
    scam_filter_enabled: bool = True
    spam_filter_enabled: bool = True
    raid_protection_enabled: bool = True
    auto_mod_level: str = "medium"
    use_native_timeout: bool = True
    spam_max_messages: int = PRESETS["medium"].spam_max_messages
    spam_window_seconds: int = PRESETS["medium"].spam_window_seconds
    raid_join_threshold: int = PRESETS["medium"].raid_join_threshold
    raid_window_seconds: int = PRESETS["medium"].raid_window_seconds
    raid_auto_lockdown: bool = False
    custom_bad_words: List[str] = field(default_factory=list)
    whitelisted_domains: List[str] = field(default_factory=list)
    ignored_channel_ids: List[int] = field(default_factory=list)
    exempt_role_ids: List[int] = field(default_factory=list)
    stats_deleted_messages: int = 0
    stats_warn_count: int = 0
    stats_mute_count: int = 0

    @classmethod
    def from_dict(cls, guild_id: int, data: Dict[str, Any]) -> "GuildConfig":
        medium = PRESETS.get("medium")
        spam_max = medium.spam_max_messages if medium else 5
        spam_win = medium.spam_window_seconds if medium else 5
        raid_thresh = medium.raid_join_threshold if medium else 5
        raid_win = medium.raid_window_seconds if medium else 10

        return cls(
            guild_id=guild_id,
            log_channel_id=data.get("log_channel_id"),
            mute_role_id=data.get("mute_role_id"),
            warn_threshold_mute=data.get("warn_threshold_mute", DEFAULT_WARN_THRESHOLD),
            mute_duration_minutes=data.get("mute_duration_minutes", DEFAULT_MUTE_MINUTES),
            profanity_filter_enabled=data.get("profanity_filter_enabled", True),
            ai_filter_enabled=data.get("ai_filter_enabled", True),
            ai_confidence_threshold=data.get("ai_confidence_threshold", DEFAULT_AI_CONFIDENCE),
            scam_filter_enabled=data.get("scam_filter_enabled", True),
            spam_filter_enabled=data.get("spam_filter_enabled", True),
            raid_protection_enabled=data.get("raid_protection_enabled", True),
            auto_mod_level=data.get("auto_mod_level", "medium"),
            use_native_timeout=data.get("use_native_timeout", True),
            spam_max_messages=data.get("spam_max_messages", spam_max),
            spam_window_seconds=data.get("spam_window_seconds", spam_win),
            raid_join_threshold=data.get("raid_join_threshold", raid_thresh),
            raid_window_seconds=data.get("raid_window_seconds", raid_win),
            raid_auto_lockdown=data.get("raid_auto_lockdown", False),
            custom_bad_words=data.get("custom_bad_words", []),
            whitelisted_domains=data.get("whitelisted_domains", []),
            ignored_channel_ids=data.get("ignored_channel_ids", []),
            exempt_role_ids=data.get("exempt_role_ids", []),
            stats_deleted_messages=data.get("stats_deleted_messages", 0),
            stats_warn_count=data.get("stats_warn_count", 0),
            stats_mute_count=data.get("stats_mute_count", 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_channel_id": self.log_channel_id,
            "mute_role_id": self.mute_role_id,
            "warn_threshold_mute": self.warn_threshold_mute,
            "mute_duration_minutes": self.mute_duration_minutes,
            "profanity_filter_enabled": self.profanity_filter_enabled,
            "ai_filter_enabled": self.ai_filter_enabled,
            "ai_confidence_threshold": self.ai_confidence_threshold,
            "scam_filter_enabled": self.scam_filter_enabled,
            "spam_filter_enabled": self.spam_filter_enabled,
            "raid_protection_enabled": self.raid_protection_enabled,
            "auto_mod_level": self.auto_mod_level,
            "use_native_timeout": self.use_native_timeout,
            "spam_max_messages": self.spam_max_messages,
            "spam_window_seconds": self.spam_window_seconds,
            "raid_join_threshold": self.raid_join_threshold,
            "raid_window_seconds": self.raid_window_seconds,
            "raid_auto_lockdown": self.raid_auto_lockdown,
            "custom_bad_words": self.custom_bad_words,
            "whitelisted_domains": self.whitelisted_domains,
            "ignored_channel_ids": self.ignored_channel_ids,
            "exempt_role_ids": self.exempt_role_ids,
            "stats_deleted_messages": self.stats_deleted_messages,
            "stats_warn_count": self.stats_warn_count,
            "stats_mute_count": self.stats_mute_count,
        }


@dataclass
class PendingUnmute:
    guild_id: int
    user_id: int
    unmute_at: float
    mute_method: str  # "timeout" | "role"
    role_id: Optional[int] = None
    reason: str = ""


class ConfigStore:
    """Local SQLite-backed high-performance configuration and moderation store."""

    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
        self._cache: Dict[int, GuildConfig] = {}
        self._init_db()

    def _init_db(self):
        """Creates local SQLite tables with WAL mode for fast parallel reads."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS guilds (
                guild_id TEXT PRIMARY KEY,
                data TEXT
            );
            CREATE TABLE IF NOT EXISTS warnings (
                id TEXT PRIMARY KEY,
                guild_id TEXT,
                user_id TEXT,
                count INTEGER,
                history TEXT
            );
            CREATE TABLE IF NOT EXISTS pending_unmutes (
                id TEXT PRIMARY KEY,
                guild_id TEXT,
                user_id TEXT,
                data TEXT
            );
        """)
        conn.commit()
        conn.close()

    async def get_config(self, guild_id: int, use_cache: bool = True) -> GuildConfig:
        if use_cache and guild_id in self._cache:
            return self._cache[guild_id]

        def _fetch():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM guilds WHERE guild_id = ?", (str(guild_id),))
            row = cursor.fetchone()
            conn.close()
            return json.loads(row[0]) if row else None

        raw_data = await asyncio.to_thread(_fetch)
        if raw_data:
            cfg = GuildConfig.from_dict(guild_id, raw_data)
        else:
            cfg = GuildConfig(guild_id=guild_id)
            apply_preset(cfg, "medium")
            await self.save_config(cfg)

        self._cache[guild_id] = cfg
        return cfg

    async def save_config(self, cfg: GuildConfig) -> None:
        def _save():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO guilds (guild_id, data) VALUES (?, ?)",
                (str(cfg.guild_id), json.dumps(cfg.to_dict()))
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_save)
        self._cache[cfg.guild_id] = cfg

    async def invalidate(self, guild_id: int) -> None:
        self._cache.pop(guild_id, None)

    async def increment_stat(self, guild_id: int, stat_name: str, count: int = 1) -> None:
        cfg = await self.get_config(guild_id)
        if stat_name == "deleted_messages":
            cfg.stats_deleted_messages += count
        elif stat_name == "warn":
            cfg.stats_warn_count += count
        elif stat_name == "mute":
            cfg.stats_mute_count += count
        await self.save_config(cfg)

    async def add_custom_word(self, guild_id: int, word: str) -> GuildConfig:
        cfg = await self.get_config(guild_id)
        normalized = word.strip().lower()
        if normalized and normalized not in cfg.custom_bad_words:
            cfg.custom_bad_words.append(normalized)
            await self.save_config(cfg)
        return cfg

    async def remove_custom_word(self, guild_id: int, word: str) -> GuildConfig:
        cfg = await self.get_config(guild_id)
        normalized = word.strip().lower()
        if normalized in cfg.custom_bad_words:
            cfg.custom_bad_words.remove(normalized)
            await self.save_config(cfg)
        return cfg

    async def add_whitelisted_domain(self, guild_id: int, domain: str) -> GuildConfig:
        cfg = await self.get_config(guild_id)
        domain_clean = domain.strip().lower()
        if domain_clean and domain_clean not in cfg.whitelisted_domains:
            cfg.whitelisted_domains.append(domain_clean)
            await self.save_config(cfg)
        return cfg

    async def remove_whitelisted_domain(self, guild_id: int, domain: str) -> GuildConfig:
        cfg = await self.get_config(guild_id)
        domain_clean = domain.strip().lower()
        if domain_clean in cfg.whitelisted_domains:
            cfg.whitelisted_domains.remove(domain_clean)
            await self.save_config(cfg)
        return cfg

    async def add_exempt_role(self, guild_id: int, role_id: int) -> GuildConfig:
        cfg = await self.get_config(guild_id)
        if role_id not in cfg.exempt_role_ids:
            cfg.exempt_role_ids.append(role_id)
            await self.save_config(cfg)
        return cfg

    async def remove_exempt_role(self, guild_id: int, role_id: int) -> GuildConfig:
        cfg = await self.get_config(guild_id)
        if role_id in cfg.exempt_role_ids:
            cfg.exempt_role_ids.remove(role_id)
            await self.save_config(cfg)
        return cfg

    async def add_warning(self, guild_id: int, user_id: int, reason: str, moderator_id: int) -> int:
        doc_id = f"{guild_id}_{user_id}"

        def _update():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT count, history FROM warnings WHERE id = ?", (doc_id,))
            row = cursor.fetchone()

            if row:
                count = row[0] + 1
                history = json.loads(row[1])
            else:
                count = 1
                history = []

            history.append({"reason": reason, "moderator_id": moderator_id, "timestamp": time.time()})

            cursor.execute(
                "INSERT OR REPLACE INTO warnings (id, guild_id, user_id, count, history) VALUES (?, ?, ?, ?, ?)",
                (doc_id, str(guild_id), str(user_id), count, json.dumps(history))
            )
            conn.commit()
            conn.close()
            return count

        count = await asyncio.to_thread(_update)
        await self.increment_stat(guild_id, "warn", 1)
        return count

    async def get_warning_count(self, guild_id: int, user_id: int) -> int:
        doc_id = f"{guild_id}_{user_id}"

        def _fetch():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT count FROM warnings WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else 0

        return await asyncio.to_thread(_fetch)

    async def clear_warnings(self, guild_id: int, user_id: int) -> None:
        doc_id = f"{guild_id}_{user_id}"

        def _clear():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO warnings (id, guild_id, user_id, count, history) VALUES (?, ?, ?, ?, ?)",
                (doc_id, str(guild_id), str(user_id), 0, json.dumps([]))
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_clear)

    async def schedule_unmute(
        self,
        guild_id: int,
        user_id: int,
        unmute_at: float,
        mute_method: str,
        *,
        role_id: Optional[int] = None,
        reason: str = "",
    ) -> None:
        doc_id = f"{guild_id}_{user_id}"
        data = {
            "unmute_at": unmute_at,
            "mute_method": mute_method,
            "role_id": role_id,
            "reason": reason,
        }

        def _save():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO pending_unmutes (id, guild_id, user_id, data) VALUES (?, ?, ?, ?)",
                (doc_id, str(guild_id), str(user_id), json.dumps(data))
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_save)
        await self.increment_stat(guild_id, "mute", 1)

    async def cancel_unmute(self, guild_id: int, user_id: int) -> None:
        doc_id = f"{guild_id}_{user_id}"

        def _delete():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pending_unmutes WHERE id = ?", (doc_id,))
            conn.commit()
            conn.close()

        await asyncio.to_thread(_delete)

    async def get_pending_unmutes(self, guild_id: Optional[int] = None) -> List[PendingUnmute]:
        def _fetch():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if guild_id is not None:
                cursor.execute("SELECT guild_id, user_id, data FROM pending_unmutes WHERE guild_id = ?", (str(guild_id),))
            else:
                cursor.execute("SELECT guild_id, user_id, data FROM pending_unmutes")
            rows = cursor.fetchall()
            conn.close()
            return rows

        rows = await asyncio.to_thread(_fetch)
        pending: List[PendingUnmute] = []
        for g_id, u_id, raw_data in rows:
            data = json.loads(raw_data) if raw_data else {}
            pending.append(
                PendingUnmute(
                    guild_id=int(g_id),
                    user_id=int(u_id),
                    unmute_at=float(data.get("unmute_at", 0)),
                    mute_method=data.get("mute_method", "role"),
                    role_id=data.get("role_id"),
                    reason=data.get("reason", ""),
                )
            )
        return pending
