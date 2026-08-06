"""
Spam and message-flood detection.

Tracks recent messages per (guild, user) in memory and flags:
  - Too many messages in a short window (flood)
  - Repeated identical / near-identical content (duplicate spam)
  - Excessive @everyone / @here mentions
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass

from filters.arabic_words import normalize_arabic

_MENTION_EVERYONE_RE = re.compile(r"@(?:everyone|here)", re.IGNORECASE)


@dataclass
class SpamCheckResult:
    is_spam: bool
    reason: str | None = None


class SpamTracker:
    """In-memory per-user message history for flood/duplicate detection."""

    def __init__(self) -> None:
        self._history: dict[tuple[int, int], list[tuple[float, str]]] = {}

    def _prune(self, key: tuple[int, int], window_seconds: float, now: float) -> list[tuple[float, str]]:
        entries = self._history.get(key, [])
        entries = [(ts, content) for ts, content in entries if now - ts <= window_seconds]
        self._history[key] = entries
        return entries

    def check(
        self,
        guild_id: int,
        user_id: int,
        content: str,
        *,
        max_messages: int,
        window_seconds: int,
        max_duplicate_count: int = 3,
    ) -> SpamCheckResult:
        now = time.time()
        key = (guild_id, user_id)
        normalized = normalize_arabic(content.strip().lower())
        entries = self._prune(key, window_seconds, now)
        entries.append((now, normalized))
        self._history[key] = entries

        if len(entries) > max_messages:
            return SpamCheckResult(True, "message_flood")

        if normalized and sum(1 for _, c in entries if c == normalized) >= max_duplicate_count:
            return SpamCheckResult(True, "duplicate_spam")

        if content and len(_MENTION_EVERYONE_RE.findall(content)) >= 2:
            return SpamCheckResult(True, "mass_mention")

        return SpamCheckResult(False)

    def clear_user(self, guild_id: int, user_id: int) -> None:
        self._history.pop((guild_id, user_id), None)
