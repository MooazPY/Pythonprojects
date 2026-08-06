import re

import discord
from discord import app_commands

from bot.commands.quran import LANGUAGE_CHOICES


class AdminCommands:
    def __init__(self, bot):
        self.bot = bot

    async def setup(self) -> None:
        @self.bot.tree.command(name="setup", description="Quick setup: channel, daily time, and language in one step")
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.choices(language=LANGUAGE_CHOICES)
        async def setup_command(
            interaction: discord.Interaction,
            channel: discord.TextChannel,
            time: str = "08:00",
            timezone: str = "UTC",
            language: app_commands.Choice[str] | None = None,
        ):
            if len(time.split(":")) != 2:
                await interaction.response.send_message("Use HH:MM format for time, e.g. 08:00.", ephemeral=True)
                return

            lang = language.value if language else self.bot.config.default_language
            settings = {
                "channel_id": str(channel.id),
                "time": time,
                "timezone": timezone,
                "language": lang,
                "brand": self.bot.config.daily_brand,
                "color": self.bot.config.default_embed_color,
            }
            self.bot.store.save_guild_settings(str(interaction.guild_id), settings)
            lang_label = self.bot.quran_service.edition_label(lang)
            embed = discord.Embed(title="Quran Bot configured", color=int(self.bot.config.default_embed_color, 16))
            embed.add_field(name="Daily channel", value=channel.mention, inline=True)
            embed.add_field(name="Daily time", value=f"{time} ({timezone})", inline=True)
            embed.add_field(name="Translation", value=lang_label, inline=True)
            embed.set_footer(text="Use /setbrand and /setcolor to customize further.")
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="setchannel", description="Set the channel for daily messages")
        @app_commands.checks.has_permissions(administrator=True)
        async def setchannel_command(interaction: discord.Interaction, channel: discord.TextChannel):
            settings = self.bot.store.get_guild_settings(str(interaction.guild_id))
            settings["channel_id"] = str(channel.id)
            self.bot.store.save_guild_settings(str(interaction.guild_id), settings)
            try:
                await interaction.response.send_message(f"Daily messages will be sent to {channel.mention}.")
            except Exception:
                if interaction.channel_id:
                    ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                    await ch.send(f"Daily messages will be sent to {channel.mention}.")

        @self.bot.tree.command(name="settime", description="Set the daily send time")
        @app_commands.checks.has_permissions(administrator=True)
        async def settime_command(interaction: discord.Interaction, time: str, timezone: str | None = None):
            if len(time.split(":")) != 2:
                try:
                    await interaction.response.send_message("Use HH:MM format, for example 08:30.")
                except Exception:
                    if interaction.channel_id:
                        ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                        await ch.send("Use HH:MM format, for example 08:30.")
                return

            settings = self.bot.store.get_guild_settings(str(interaction.guild_id))
            settings["time"] = time
            settings["timezone"] = timezone or self.bot.config.default_timezone
            self.bot.store.save_guild_settings(str(interaction.guild_id), settings)
            try:
                await interaction.response.send_message(f"Daily time set to {time} in {settings['timezone']}.")
            except Exception:
                if interaction.channel_id:
                    ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                    await ch.send(f"Daily time set to {time} in {settings['timezone']}.")

        @self.bot.tree.command(name="setlanguage", description="Set the default translation language")
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.choices(language=LANGUAGE_CHOICES)
        async def setlanguage_command(interaction: discord.Interaction, language: app_commands.Choice[str]):
            settings = self.bot.store.get_guild_settings(str(interaction.guild_id))
            settings["language"] = language.value
            self.bot.store.save_guild_settings(str(interaction.guild_id), settings)
            label = self.bot.quran_service.edition_label(language.value)
            try:
                await interaction.response.send_message(f"Default translation set to **{label}**.")
            except Exception:
                if interaction.channel_id:
                    ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                    await ch.send(f"Default translation set to **{label}**.")

        @self.bot.tree.command(name="setbrand", description="Set the brand text used in daily messages")
        @app_commands.checks.has_permissions(administrator=True)
        async def setbrand_command(interaction: discord.Interaction, brand: str):
            settings = self.bot.store.get_guild_settings(str(interaction.guild_id))
            settings["brand"] = brand
            self.bot.store.save_guild_settings(str(interaction.guild_id), settings)
            try:
                await interaction.response.send_message(f"Daily brand text set to: {brand}")
            except Exception:
                if interaction.channel_id:
                    ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                    await ch.send(f"Daily brand text set to: {brand}")

        @self.bot.tree.command(name="setcolor", description="Set the embed color for Quran bot messages")
        @app_commands.checks.has_permissions(administrator=True)
        async def setcolor_command(interaction: discord.Interaction, color: str):
            normalized = color.lstrip("#")
            if not re.fullmatch(r"[0-9A-Fa-f]{6}", normalized):
                try:
                    await interaction.response.send_message(
                        "Please provide a valid 6-digit hex color like #1E8DD3 or 1E8DD3."
                    )
                except Exception:
                    if interaction.channel_id:
                        ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                        await ch.send("Please provide a valid 6-digit hex color like #1E8DD3 or 1E8DD3.")
                return
            settings = self.bot.store.get_guild_settings(str(interaction.guild_id))
            settings["color"] = normalized.upper()
            self.bot.store.save_guild_settings(str(interaction.guild_id), settings)
            try:
                await interaction.response.send_message(f"Embed color set to #{normalized.upper()}.")
            except Exception:
                if interaction.channel_id:
                    ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                    await ch.send(f"Embed color set to #{normalized.upper()}.")

        @self.bot.tree.command(name="viewsettings", description="Show this server's Quran bot settings")
        @app_commands.checks.has_permissions(administrator=True)
        async def viewsettings_command(interaction: discord.Interaction):
            settings = self.bot.store.get_guild_settings(str(interaction.guild_id))
            defaults = {
                "channel_id": self.bot.config.default_channel_id,
                "time": self.bot.config.default_time,
                "timezone": self.bot.config.default_timezone,
                "language": self.bot.config.default_language,
            }
            merged = {**defaults, **settings}
            try:
                await interaction.response.send_message(
                    f"Current settings:\n"
                    f"Channel: {merged.get('channel_id')}\n"
                    f"Daily time: {merged.get('time')}\n"
                    f"Timezone: {merged.get('timezone')}\n"
                    f"Translation language: {merged.get('language')}\n"
                    f"Embed color: #{merged.get('color') or self.bot.config.default_embed_color}"
                )
            except Exception:
                if interaction.channel_id:
                    ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                    await ch.send(
                        f"Current settings:\n"
                        f"Channel: {merged.get('channel_id')}\n"
                        f"Daily time: {merged.get('time')}\n"
                        f"Timezone: {merged.get('timezone')}\n"
                        f"Translation language: {merged.get('language')}\n"
                        f"Embed color: #{merged.get('color') or self.bot.config.default_embed_color}"
                    )

        @self.bot.tree.command(name="synccommands", description="Force sync slash commands to Discord")
        @app_commands.checks.has_permissions(administrator=True)
        async def synccommands_command(interaction: discord.Interaction):
            deferred = True
            try:
                await interaction.response.defer(thinking=True)
            except Exception:
                deferred = False

            if interaction.guild_id is not None:
                guild = discord.Object(id=int(interaction.guild_id))
                synced = await self.bot.tree.sync(guild=guild)
                message = f"Synced {len(synced)} slash command(s) to guild {interaction.guild_id}."
            elif self.bot.config.default_guild_id:
                guild = discord.Object(id=int(self.bot.config.default_guild_id))
                synced = await self.bot.tree.sync(guild=guild)
                message = f"Synced {len(synced)} slash command(s) to guild {self.bot.config.default_guild_id}."
            else:
                synced = await self.bot.tree.sync()
                message = f"Synced {len(synced)} global slash command(s)."

            try:
                if deferred:
                    await interaction.followup.send(message)
                else:
                    await interaction.response.send_message(message)
            except Exception:
                if interaction.channel_id:
                    ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                    await ch.send(message)
