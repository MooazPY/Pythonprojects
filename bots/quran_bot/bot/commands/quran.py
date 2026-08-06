import discord
from discord import app_commands

from bot.services.quran_api import QuranApiError

LANGUAGE_CHOICES = [
    app_commands.Choice(name="English (Sahih)", value="en"),
    app_commands.Choice(name="French", value="fr"),
    app_commands.Choice(name="Urdu", value="ur"),
    app_commands.Choice(name="Turkish", value="tr"),
    app_commands.Choice(name="Indonesian", value="id"),
    app_commands.Choice(name="German", value="de"),
    app_commands.Choice(name="Spanish", value="es"),
]

RECITER_CHOICES = [
    app_commands.Choice(name="Mishary Alafasy", value="alafasy"),
    app_commands.Choice(name="Mahmoud Khalil Al-Husary", value="husary"),
    app_commands.Choice(name="Mohammad Siddiq Al-Minshawi", value="minshawi"),
    app_commands.Choice(name="Abdurrahman As-Sudais", value="sudais"),
]


class QuranCommands:
    def __init__(self, bot):
        self.bot = bot

    @property
    def service(self):
        return self.bot.quran_service

    def _get_embed_color(self, guild_id: str | None) -> int:
        settings = self.bot.store.get_guild_settings(str(guild_id)) if guild_id else {}
        color_hex = settings.get("color") or self.bot.config.default_embed_color
        try:
            return int(color_hex.lstrip("#"), 16)
        except ValueError:
            return int(self.bot.config.default_embed_color, 16)

    def _build_ayah_embed(self, payload: dict, translation: str | None, language: str, brand: str, color: int) -> discord.Embed:
        surah = payload["surah"]
        title = f"{brand} — Surah {surah['number']}:{payload['numberInSurah']}"
        description = payload.get("text", "Arabic text unavailable.")
        edition_label = self.service.edition_label(language)

        embed = discord.Embed(title=title, description=description, color=color)
        embed.add_field(
            name="Surah",
            value=f"{surah['number']} — {surah.get('englishName', surah.get('name', 'Unknown'))}",
            inline=True,
        )
        embed.add_field(name="Ayah", value=str(payload.get("numberInSurah", "?")), inline=True)

        if translation:
            embed.add_field(name=f"Translation ({edition_label})", value=translation[:1024], inline=False)

        embed.set_footer(text=f"{brand} • Quran Bot")
        return embed

    async def _send_embed_or_error(self, interaction: discord.Interaction, deferred: bool, embed=None, error: str | None = None) -> None:
        content = None
        if error:
            content = error
        try:
            if deferred:
                await interaction.followup.send(content=content, embed=embed)
            else:
                await interaction.response.send_message(content=content, embed=embed)
        except Exception:
            if interaction.channel_id:
                ch = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
                await ch.send(content=content, embed=embed)

    async def setup(self) -> None:
        @self.bot.tree.command(name="quran", description="Send a Quran ayah")
        @app_commands.choices(language=LANGUAGE_CHOICES)
        async def quran_command(
            interaction: discord.Interaction,
            surah: int | None = None,
            ayah: int | None = None,
            language: app_commands.Choice[str] | None = None,
        ):
            lang = (language.value if language else None) or self.bot.store.get_guild_settings(str(interaction.guild_id)).get("language") or self.bot.config.default_language
            deferred = True
            try:
                await interaction.response.defer(thinking=True)
            except Exception:
                deferred = False

            try:
                if surah is None or ayah is None:
                    payload = await self.service.get_random_ayah(translation="ar")
                else:
                    payload = await self.service.get_ayah(surah, ayah, translation="ar")

                translation_payload = await self.service.get_translation(payload["surah"]["number"], payload["numberInSurah"], language=lang)
                translation = translation_payload.get("text") if translation_payload else None
                brand = self.bot.store.get_guild_settings(str(interaction.guild_id)).get("brand") or self.bot.config.daily_brand
                embed = self._build_ayah_embed(payload, translation, lang, brand, self._get_embed_color(interaction.guild_id))
                self.bot.store.increment_command_count(str(interaction.guild_id), "quran")
                await self._send_embed_or_error(interaction, deferred, embed=embed)
            except QuranApiError as exc:
                await self._send_embed_or_error(interaction, deferred, error=str(exc))

        @self.bot.tree.command(name="translation", description="Show a translation for a Quran ayah")
        @app_commands.choices(language=LANGUAGE_CHOICES)
        async def translation_command(
            interaction: discord.Interaction,
            surah: int,
            ayah: int,
            language: app_commands.Choice[str] | None = None,
        ):
            lang = (language.value if language else None) or self.bot.store.get_guild_settings(str(interaction.guild_id)).get("language") or self.bot.config.default_language
            deferred = True
            try:
                await interaction.response.defer(thinking=True)
            except Exception:
                deferred = False

            try:
                payload = await self.service.get_ayah(surah, ayah, translation="ar")
                translation_payload = await self.service.get_translation(surah, ayah, language=lang)
                translation = translation_payload.get("text") if translation_payload else None
                brand = self.bot.store.get_guild_settings(str(interaction.guild_id)).get("brand") or self.bot.config.daily_brand
                embed = self._build_ayah_embed(payload, translation, lang, brand, self._get_embed_color(interaction.guild_id))
                self.bot.store.increment_command_count(str(interaction.guild_id), "translation")
                await self._send_embed_or_error(interaction, deferred, embed=embed)
            except QuranApiError as exc:
                await self._send_embed_or_error(interaction, deferred, error=str(exc))

        @self.bot.tree.command(name="recite", description="Get an audio recitation link for an ayah")
        @app_commands.choices(reciter=RECITER_CHOICES)
        async def recite_command(
            interaction: discord.Interaction,
            surah: int,
            ayah: int,
            reciter: app_commands.Choice[str] | None = None,
        ):
            reciter_id = reciter.value if reciter else "alafasy"
            deferred = True
            try:
                await interaction.response.defer(thinking=True)
            except Exception:
                deferred = False

            try:
                surah_data = await self.service.get_surah_info(surah)
                if ayah < 1 or ayah > surah_data.get("numberOfAyahs", 0):
                    await self._send_embed_or_error(interaction, deferred, error=f"Surah {surah} has {surah_data.get('numberOfAyahs', '?')} ayahs.")
                    return

                audio_url = await self.service.get_recitation_url(surah, ayah, reciter_id)
                if not audio_url:
                    await self._send_embed_or_error(interaction, deferred, error="Recitation audio is unavailable right now.")
                    return

                reciter_name = reciter.name if reciter else "Mishary Alafasy"
                embed = discord.Embed(
                    title=f"Recitation — Surah {surah}:{ayah}",
                    description=f"**{surah_data.get('englishName', 'Unknown')}** — Ayah {ayah}",
                    color=self._get_embed_color(interaction.guild_id),
                )
                embed.add_field(name="Reciter", value=reciter_name, inline=True)
                embed.add_field(name="Listen", value=f"[Open audio]({audio_url})", inline=True)
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="Play recitation", url=audio_url, emoji="🔊"))
                self.bot.store.increment_command_count(str(interaction.guild_id), "recite")

                if deferred:
                    await interaction.followup.send(embed=embed, view=view)
                else:
                    await interaction.response.send_message(embed=embed, view=view)
            except QuranApiError as exc:
                await self._send_embed_or_error(interaction, deferred, error=str(exc))

        @self.bot.tree.command(name="help", description="Show help for the bot")
        async def help_command(interaction: discord.Interaction):
            embed = discord.Embed(title="Quran Bot — Commands", color=self._get_embed_color(interaction.guild_id))
            embed.add_field(
                name="Quran",
                value="`/quran` — random or specific ayah\n"
                "`/translation` — ayah with translation\n"
                "`/recite` — audio recitation link\n"
                "`/surahinfo` — chapter info\n"
                "`/status` — server settings & stats",
                inline=False,
            )
            embed.add_field(
                name="Admin",
                value="`/setup` — quick first-time configuration\n"
                "`/setchannel` `/settime` `/setlanguage` `/setbrand` `/setcolor` `/viewsettings` `/synccommands`",
                inline=False,
            )
            embed.set_footer(text="Languages: en, fr, ur, tr, id, de, es • Reciters: Alafasy, Husary, Minshawi, Sudais")
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="status", description="Show this server's Quran bot status and usage stats")
        async def status_command(interaction: discord.Interaction):
            settings = self.bot.store.get_guild_settings(str(interaction.guild_id))
            stats = self.bot.store.get_command_stats(str(interaction.guild_id))
            defaults = {
                "channel_id": self.bot.config.default_channel_id,
                "time": self.bot.config.default_time,
                "timezone": self.bot.config.default_timezone,
                "language": self.bot.config.default_language,
                "color": self.bot.config.default_embed_color,
                "brand": self.bot.config.daily_brand,
            }
            merged = {**defaults, **settings}
            lang_label = self.service.edition_label(merged.get("language", "en"))
            stats_text = "\n".join(f"{cmd}: {count}" for cmd, count in stats.items()) or "No command usage data yet."
            embed = discord.Embed(title="Quran Bot Status", color=self._get_embed_color(interaction.guild_id))
            embed.add_field(name="Channel", value=merged.get("channel_id") or "None", inline=True)
            embed.add_field(name="Time", value=merged.get("time"), inline=True)
            embed.add_field(name="Timezone", value=merged.get("timezone"), inline=True)
            embed.add_field(name="Language", value=lang_label, inline=True)
            embed.add_field(name="Brand", value=merged.get("brand"), inline=False)
            embed.add_field(name="Embed Color", value=f"#{merged.get('color')}", inline=False)
            embed.add_field(name="Command Stats", value=stats_text, inline=False)
            self.bot.store.increment_command_count(str(interaction.guild_id), "status")
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="surahinfo", description="Show metadata for a chapter of the Quran")
        async def surahinfo_command(interaction: discord.Interaction, surah: int):
            deferred = True
            try:
                await interaction.response.defer(thinking=True)
            except Exception:
                deferred = False
            try:
                surah_data = await self.service.get_surah_info(surah)
                embed = discord.Embed(
                    title=f"Surah {surah}: {surah_data.get('englishName', 'Unknown')}",
                    description=surah_data.get("englishNameTranslation", ""),
                    color=self._get_embed_color(interaction.guild_id),
                )
                embed.add_field(name="Arabic Name", value=surah_data.get("name", "—"), inline=True)
                embed.add_field(name="Ayahs", value=str(surah_data.get("numberOfAyahs", "?")), inline=True)
                embed.add_field(name="Revelation", value=surah_data.get("revelationType", "Unknown"), inline=True)
                embed.add_field(
                    name="Bismillah",
                    value="Included" if surah_data.get("bismillahPre", False) else "Not included",
                    inline=False,
                )
                self.bot.store.increment_command_count(str(interaction.guild_id), "surahinfo")
                await self._send_embed_or_error(interaction, deferred, embed=embed)
            except QuranApiError as exc:
                await self._send_embed_or_error(interaction, deferred, error=str(exc))
