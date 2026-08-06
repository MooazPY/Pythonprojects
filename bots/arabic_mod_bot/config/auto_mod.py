"""Auto-mod sensitivity presets applied via /config set-level."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AutoModPreset:
    warn_threshold_mute: int
    mute_duration_minutes: int
    spam_max_messages: int
    spam_window_seconds: int
    raid_join_threshold: int
    raid_window_seconds: int


PRESETS: dict[str, AutoModPreset] = {
    "low": AutoModPreset(
        warn_threshold_mute=5,
        mute_duration_minutes=15,
        spam_max_messages=10,
        spam_window_seconds=12,
        raid_join_threshold=12,
        raid_window_seconds=60,
    ),
    "medium": AutoModPreset(
        warn_threshold_mute=3,
        mute_duration_minutes=30,
        spam_max_messages=6,
        spam_window_seconds=8,
        raid_join_threshold=8,
        raid_window_seconds=45,
    ),
    "high": AutoModPreset(
        warn_threshold_mute=2,
        mute_duration_minutes=60,
        spam_max_messages=4,
        spam_window_seconds=6,
        raid_join_threshold=5,
        raid_window_seconds=30,
    ),
}

VALID_LEVELS = frozenset(PRESETS)


class _AutoModConfig(Protocol):
    auto_mod_level: str
    warn_threshold_mute: int
    mute_duration_minutes: int
    spam_max_messages: int
    spam_window_seconds: int
    raid_join_threshold: int
    raid_window_seconds: int


def apply_preset(cfg: _AutoModConfig, level: str) -> _AutoModConfig:
    preset = PRESETS[level]
    cfg.auto_mod_level = level
    cfg.warn_threshold_mute = preset.warn_threshold_mute
    cfg.mute_duration_minutes = preset.mute_duration_minutes
    cfg.spam_max_messages = preset.spam_max_messages
    cfg.spam_window_seconds = preset.spam_window_seconds
    cfg.raid_join_threshold = preset.raid_join_threshold
    cfg.raid_window_seconds = preset.raid_window_seconds
    return cfg
