import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)


@dataclass
class BotConfig:
    token: str
    command_prefix: str = "$"
    daily_brand: str = "الورد اليومي"
    default_timezone: str = "UTC"
    default_time: str = "08:00"
    default_language: str = "en"
    default_channel_id: str | None = None
    default_embed_color: str = "1E8DD3"
    default_guild_id: str | None = None
    guild_settings_path: str | None = None
    intents: str | None = None

    @classmethod
    def from_env(cls) -> "BotConfig":
        token = os.getenv("DIS_TOKEN", "").strip()
        if not token:
            raise RuntimeError("DIS_TOKEN is not set in the .env file")

        return cls(
            token=token,
            command_prefix=os.getenv("COMMAND_PREFIX", "$"),
            daily_brand=os.getenv("DAILY_BRAND", "الورد اليومي"),
            default_timezone=os.getenv("DEFAULT_TIMEZONE", "UTC"),
            default_time=os.getenv("DEFAULT_TIME", "08:00"),
            default_language=os.getenv("DEFAULT_LANGUAGE", "en"),
            default_channel_id=os.getenv("DISCORD_CHANNEL_ID"),
            default_embed_color=os.getenv("DEFAULT_EMBED_COLOR", "1E8DD3"),
            default_guild_id=os.getenv("DISCORD_GUILD_ID"),
            guild_settings_path=os.getenv("GUILD_SETTINGS_PATH"),
        )
