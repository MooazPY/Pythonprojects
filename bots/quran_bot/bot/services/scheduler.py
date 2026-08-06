from __future__ import annotations

import asyncio
import logging
from datetime import datetime, time, timezone
from datetime import tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Optional

import discord

from bot.config import BotConfig
from bot.services.storage import GuildSettingsStore

logger = logging.getLogger(__name__)


class DailyScheduler:
    CHECK_INTERVAL_SECONDS = 30

    def __init__(self, bot: discord.Client, store: GuildSettingsStore, config: BotConfig):
        self.bot = bot
        self.store = store
        self.config = config
        self._task: Optional[asyncio.Task[None]] = None

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())
            logger.info("Daily scheduler started")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None
        logger.info("Daily scheduler stopped")

    async def _run(self) -> None:
        while True:
            try:
                await self._check_schedules()
            except Exception as exc:
                logger.exception("Daily scheduler error: %s", exc)
            await asyncio.sleep(self.CHECK_INTERVAL_SECONDS)

    async def _check_schedules(self) -> None:
        utc_now = datetime.now(tz=timezone.utc)
        for guild in list(self.bot.guilds):
            settings = self.store.get_guild_settings(str(guild.id))
            send_time = self._parse_time(settings.get("time") or self.config.default_time)
            configured_timezone = self._resolve_timezone(settings.get("timezone") or self.config.default_timezone)
            if send_time is None or configured_timezone is None:
                continue

            local_now = utc_now.astimezone(configured_timezone)
            if local_now.time().replace(second=0, microsecond=0) != send_time:
                continue

            last_sent_date = settings.get("last_sent_date")
            if last_sent_date == local_now.date().isoformat():
                continue

            try:
                logger.info("Sending scheduled daily message for guild %s at %s", guild.id, local_now.isoformat())
                await self.bot.send_daily_message(str(guild.id))
                settings["last_sent_date"] = local_now.date().isoformat()
                self.store.save_guild_settings(str(guild.id), settings)
            except Exception as exc:
                logger.exception("Failed to send scheduled message for guild %s: %s", guild.id, exc)

    def _parse_time(self, value: str) -> Optional[time]:
        try:
            hours, minutes = value.split(":")
            return time(int(hours), int(minutes))
        except ValueError:
            logger.warning("Invalid configured time '%s'; expected HH:MM", value)
            return None

    def _resolve_timezone(self, timezone_name: str) -> Optional[tzinfo]:
        if timezone_name.upper() == "UTC":
            return timezone.utc

        try:
            return ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            logger.warning("Invalid timezone '%s'; defaulting to UTC", timezone_name)
            return timezone.utc
