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

from web_dashboard import WebDashboardServer

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
        self.web_dashboard = WebDashboardServer(self, port=int(os.environ.get("PORT", "8080")))

    async def setup_hook(self):
        self.tree.on_error = self.on_tree_error
        for extension in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(extension)
                logger.info("Loaded extension: %s", extension)
            except Exception:
                logger.exception("Failed to load extension: %s", extension)

        synced = await self.tree.sync()
        logger.info("Synced %d global slash command(s).", len(synced))

        # Register persistent views so buttons work across bot restarts
        from cogs.moderation import PersistentAppealView
        self.add_view(PersistentAppealView(self.config_store))

        await self.web_dashboard.start()

    async def on_ready(self):
        logger.info("Haris Pro is online and logged in as %s (ID: %d)", self.user, self.user.id)
        logger.info("Active in %d guild(s).", len(self.guilds))

        # Sync slash commands to all active guilds for instant availability
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info("Instantly synced slash commands to guild: %s", guild.name)
            except Exception as e:
                logger.debug("Could not sync to guild %s: %s", guild.name, e)

        await restore_pending_unmutes(self, self.config_store)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="حماية السيرفر الذكية 🛡️ | /setup"
            )
        )

    async def on_tree_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Global error handler for all slash commands with user-friendly Arabic messages."""
        if isinstance(error, discord.app_commands.MissingPermissions):
            msg = "❌ **خطأ:** ليس لديك الصلاحية الكافية لاستخدام هذا الأمر."
        elif isinstance(error, discord.app_commands.MissingRole):
            msg = f"❌ **خطأ:** تحتاج إلى رتبة `{error.missing_role}` لاستخدام هذا الأمر."
        elif isinstance(error, discord.app_commands.CommandOnCooldown):
            msg = f"⏳ **الأمر قيد الانتظار:** برجاء الانتظار `{error.retry_after:.1f}` ثانية قبل إعادة الاستخدام."
        elif isinstance(error, discord.app_commands.CheckFailure):
            msg = "❌ **خطأ:** لا تملك الصلاحيات اللازمة لاستخدام هذا الأمر."
        else:
            logger.error("Unhandled slash command error in command '%s': %s", interaction.command.name if interaction.command else "Unknown", error, exc_info=error)
            msg = "❌ **خطأ غير متوقع:** حدث خطأ أثناء تنفيذ الأمر."

        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except discord.HTTPException:
            pass

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
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not token or "YOUR_DISCORD_BOT_TOKEN" in token or "your_discord_bot_token" in token:
        logger.error("DISCORD_BOT_TOKEN is missing or set to placeholder string in .env file.")
        print("\n❌ [خطأ]: لم يتم تعيين توكن البوت الصحيح في ملف .env")
        print("برجاء فتح ملف .env واستبدال YOUR_DISCORD_BOT_TOKEN_HERE بتوكن البوت الخاص بك من Discord Developer Portal.\n")
        raise SystemExit(1)

    bot = HarisBot()
    bot.run(token)


if __name__ == "__main__":
    main()