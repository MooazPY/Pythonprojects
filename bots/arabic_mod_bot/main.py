"""
Haris Pro — Advanced Commercial Arabic Moderation & Anti-Scam Discord Bot.

Environment variables required:
    DISCORD_BOT_TOKEN                 - Bot token from Discord Developer Portal
    HUGGINGFACE_TOKEN (Optional)      - Hugging Face API token for AI toxicity classifier
"""

from __future__ import annotations

import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config.db_config import ConfigStore
from moderation import restore_pending_unmutes

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("haris")

INITIAL_EXTENSIONS = [
    "cogs.moderation",
    "cogs.setup",
]


class HarisBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

        self.config_store = ConfigStore()

    async def setup_hook(self):
        for extension in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(extension)
                logger.info("Loaded extension: %s", extension)
            except Exception:
                logger.exception("Failed to load extension: %s", extension)

        synced = await self.tree.sync()
        logger.info("Synced %d slash command(s).", len(synced))

    async def on_ready(self):
        logger.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        logger.info("Active in %d guild(s).", len(self.guilds))
        await restore_pending_unmutes(self, self.config_store)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="حماية السيرفر الذكية 🛡️ | /setup"
            )
        )

    async def on_guild_join(self, guild: discord.Guild):
        """Automatically creates a dedicated control channel named 'حارس-الإشراف' when joining a server."""
        logger.info("Joined new guild: %s (ID: %s)", guild.name, guild.id)

        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }

            channel = await guild.create_text_channel(
                name="حارس-الإشراف",
                topic="القناة الرسمية لسجلات وتحكم بوت حارس Pro الذكي.",
                overwrites=overwrites
            )

            embed = discord.Embed(
                title=f"👋 مرحباً بكم في {guild.name}!",
                description=(
                    "شكرًا لإضافتي لحماية وإدارة السيرفر بنظام الذكاء الاصطناعي.\n\n"
                    "⚙️ **البدء السريع:**\n"
                    "• استخدم الأمر `/setup` لضبط إعدادات السيرفر.\n"
                    "• استخدم الأمر `/setup_ai` لإدارة تصفية الذكاء الاصطناعي.\n"
                    "• استخدم الأمر `/analyze_text` لاختبار قوة التحليل الذكي."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="حارس Pro — نظام الحماية العربي المتكامل")
            await channel.send(embed=embed)
            logger.info("Successfully created channel 'حارس-الإشراف' in %s", guild.name)

        except discord.Forbidden:
            logger.warning("Missing permissions to create channels in guild: %s", guild.name)
        except Exception as e:
            logger.error("Failed to create channel for guild %s: %s", guild.name, e)


def main():
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("DISCORD_BOT_TOKEN environment variable is not set.")

    bot = HarisBot()
    bot.run(token)


if __name__ == "__main__":
    main()