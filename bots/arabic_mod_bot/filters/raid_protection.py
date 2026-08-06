"""
Raid protection: detect mass joins in a short window and alert moderators.

When the threshold is exceeded the bot posts an alert to the configured log
channel. Optional auto-lockdown sets @everyone send_messages=False on all
text channels (requires Manage Channels).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

logger = logging.getLogger("arabic_mod_bot.raid")


@dataclass
class RaidCheckResult:
    is_raid: bool
    join_count: int = 0


class RaidTracker:
    def __init__(self) -> None:
        self._joins: dict[int, list[float]] = {}
        self._lockdown_active: set[int] = set()

    def record_join(self, guild_id: int, window_seconds: int) -> RaidCheckResult:
        now = time.time()
        joins = [ts for ts in self._joins.get(guild_id, []) if now - ts <= window_seconds]
        joins.append(now)
        self._joins[guild_id] = joins
        return RaidCheckResult(False, len(joins))

    def check_threshold(
        self, guild_id: int, threshold: int, window_seconds: int
    ) -> RaidCheckResult:
        now = time.time()
        joins = [ts for ts in self._joins.get(guild_id, []) if now - ts <= window_seconds]
        count = len(joins)
        return RaidCheckResult(count >= threshold, count)

    def mark_lockdown(self, guild_id: int) -> None:
        self._lockdown_active.add(guild_id)

    def is_lockdown(self, guild_id: int) -> bool:
        return guild_id in self._lockdown_active

    def clear_lockdown(self, guild_id: int) -> None:
        self._lockdown_active.discard(guild_id)
