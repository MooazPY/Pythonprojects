import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import discord
from discord.ext import commands

from bot.commands.admin import AdminCommands
from bot.commands.quran import QuranCommands
from bot.config import BotConfig
from bot.services.quran_api import QuranApiError, QuranService
from bot.services.scheduler import DailyScheduler
from bot.services.storage import GuildSettingsStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    force=True,
    handlers=[
        logging.FileHandler("C:/Users/Mooaz/AppData/Local/Temp/discord_bot.log", mode="w", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class QuranBot(commands.Bot):
    def __init__(self, config: BotConfig, store: GuildSettingsStore):
        intents = discord.Intents.default()
        super().__init__(command_prefix=config.command_prefix, intents=intents)
        self.config = config
        self.store = store
        self.quran_service = QuranService()
        self.quran_commands = QuranCommands(self)
        self.admin_commands = AdminCommands(self)
        self.daily_scheduler = DailyScheduler(self, store, config)

    async def _log_registered_commands(self) -> None:
        commands = [command.name for command in self.tree.walk_commands() if command.name]
        logger.info("Registered slash commands: %s", ", ".join(sorted(commands)))

    async def setup_hook(self) -> None:
        await self.quran_commands.setup()
        await self.admin_commands.setup()

    async def on_ready(self) -> None:
        logger.info("Logged in as %s", self.user)
        await self._log_registered_commands()
        await self._sync_commands()
        self.daily_scheduler.start()

    async def _sync_commands(self) -> None:
        try:
            tree_commands = list(self.tree.walk_commands())
            logger.info("Tree contains %d commands before sync", len(tree_commands))
            for cmd in tree_commands:
                logger.info("  Tree command: %s (guild_ids=%s)", cmd.name, getattr(cmd, "guild_ids", None))

            guild_id = self.config.default_guild_id
            if not guild_id:
                logger.info("No default_guild_id configured, skipping guild command registration")
                return

            logger.info("Registering %d commands to guild %s via direct API", len(tree_commands), guild_id)
            payload = [cmd.to_dict(self.tree) for cmd in tree_commands]
            try:
                result = await self.http.bulk_upsert_guild_commands(
                    application_id=int(self.application_id),
                    guild_id=int(guild_id),
                    payload=payload,
                )
                registered = [item.get("name", "?") for item in result]
                logger.info("  Registered: %s", ", ".join(registered))
                logger.info("Guild registration complete: %d/%d commands registered", len(registered), len(tree_commands))
            except Exception as exc:
                logger.error("Bulk guild registration failed: %s", exc, exc_info=True)
                raise
        except Exception as exc:
            logger.error("Command sync failed: %s", exc, exc_info=True)
            raise

    async def on_connect(self) -> None:
        logger.info("Connected to Discord gateway")

    async def on_disconnect(self) -> None:
        logger.warning("Disconnected from Discord gateway")

    async def close(self) -> None:
        if hasattr(self, "daily_scheduler"):
            await self.daily_scheduler.stop()
        await self.quran_service.close()
        await super().close()

    def _format_ayah_data(self, payload: dict) -> dict:
        surah_info = payload.get("surah") or {}
        return {
            "surah_number": surah_info.get("number") or payload.get("surah"),
            "surah_name": surah_info.get("englishName") or surah_info.get("name") or "Unknown",
            "english_name": surah_info.get("englishNameTranslation", ""),
            "ayah": payload.get("numberInSurah"),
            "arabic": payload.get("text", ""),
        }

    def _build_ayah_embed(self, payload: dict, translation: str | None, edition_label: str, brand: str) -> discord.Embed:
        ayah_data = self._format_ayah_data(payload)
        title = f"{brand} — Surah {ayah_data['surah_number']}:{ayah_data['ayah']}"
        description = ayah_data["arabic"] or "Arabic text unavailable."
        embed = discord.Embed(title=title, description=description, color=0x1E8DD3)
        embed.add_field(
            name="Surah",
            value=f"{ayah_data['surah_number']} — {ayah_data['surah_name']}",
            inline=True,
        )
        embed.add_field(name="Ayah", value=str(ayah_data["ayah"]), inline=True)

        if translation:
            embed.add_field(
                name=f"Translation ({edition_label})",
                value=translation[:1024],
                inline=False,
            )

        embed.set_footer(text=f"{brand} • Quran Bot")
        embed.timestamp = datetime.now(timezone.utc)
        return embed

    async def send_daily_message(self, guild_id: str | None = None) -> None:
        if guild_id is None:
            channel_id = self.config.default_channel_id
        else:
            settings = self.store.get_guild_settings(guild_id)
            channel_id = settings.get("channel_id") or self.config.default_channel_id

        if not channel_id:
            logger.warning("No daily channel configured for guild %s", guild_id or "default")
            return

        channel = self.get_channel(int(channel_id))
        if channel is None:
            try:
                channel = await self.fetch_channel(int(channel_id))
            except discord.NotFound:
                logger.error("Channel %s was not found", channel_id)
                return
            except discord.Forbidden:
                logger.error("The bot lacks permission to access channel %s", channel_id)
                return

        try:
            settings = self.store.get_guild_settings(guild_id) if guild_id else {}
            language = settings.get("language") or self.config.default_language
            brand = settings.get("brand") or self.config.daily_brand
            color_hex = settings.get("color") or self.config.default_embed_color
            try:
                color = int(color_hex.lstrip("#"), 16)
            except ValueError:
                color = int(self.config.default_embed_color, 16)

            payload = await self.quran_service.get_random_ayah(translation="ar")
            translation_payload = await self.quran_service.get_translation(
                payload["surah"]["number"], payload["numberInSurah"], language=language
            )
            translation = translation_payload.get("text") if translation_payload else None
            edition_label = self.quran_service.edition_label(language)
            embed = self._build_ayah_embed(payload, translation, edition_label, brand)
            embed.colour = color
            await channel.send(embed=embed)
            self.store.increment_command_count(guild_id, "daily")
            logger.info("Daily message sent to %s", channel_id)
        except QuranApiError as exc:
            logger.error("Daily message failed: %s", exc)
        except discord.Forbidden:
            logger.error("Missing permission to send messages in channel %s", channel_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Quran Discord bot")
    parser.add_argument("--daily", action="store_true", help="Send one daily message then exit")
    parser.add_argument("--serve", action="store_true", help="Stay connected and serve slash commands")
    parser.add_argument("--print-url", action="store_true", help="Print a sample Quran page URL and exit")
    return parser.parse_args()


async def run_daily(config: BotConfig, store: GuildSettingsStore) -> None:
    logger.info("Starting daily mode")
    bot = QuranBot(config, store)
    await bot.login(config.token)
    connect_task = asyncio.create_task(bot.connect(reconnect=False))
    try:
        logger.info("Waiting for Discord ready state")
        await asyncio.wait_for(bot.wait_until_ready(), timeout=20)
        logger.info("Discord ready; sending daily message")
        if bot.guilds:
            for guild in bot.guilds:
                await bot.send_daily_message(str(guild.id))
        else:
            await bot.send_daily_message(None)
    except asyncio.TimeoutError:
        logger.error("The bot did not become ready within 20 seconds. Check the Discord token, network access, and bot invitation status.")
        raise
    except Exception as exc:
        logger.exception("Daily mode failed: %s", exc)
        raise
    finally:
        connect_task.cancel()
        try:
            await connect_task
        except asyncio.CancelledError:
            pass
        if bot.is_closed():
            return
        await bot.close()


async def run_serve(config: BotConfig, store: GuildSettingsStore) -> None:
    bot = QuranBot(config, store)
    try:
        await bot.start(config.token)
    finally:
        await bot.close()


def main() -> None:
    args = parse_args()
    if args.print_url:
        print("https://api.alquran.cloud/v1/ayah/262")
        return

    config = BotConfig.from_env()
    store = GuildSettingsStore(config.guild_settings_path)

    try:
        if args.daily:
            asyncio.run(run_daily(config, store))
        elif args.serve:
            asyncio.run(run_serve(config, store))
        else:
            print("Please choose --daily or --serve. --print-url is for debugging only.")
            sys.exit(2)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
