"""Unit tests for auto-mod presets."""

from config.auto_mod import PRESETS, apply_preset
from config.db_config import GuildConfig


def test_apply_high_preset():
    cfg = GuildConfig(guild_id=1)
    apply_preset(cfg, "high")
    assert cfg.auto_mod_level == "high"
    assert cfg.warn_threshold_mute == PRESETS["high"].warn_threshold_mute
    assert cfg.spam_max_messages == PRESETS["high"].spam_max_messages


def test_apply_low_preset():
    cfg = GuildConfig(guild_id=1)
    apply_preset(cfg, "low")
    assert cfg.warn_threshold_mute == 5
    assert cfg.mute_duration_minutes == 15
