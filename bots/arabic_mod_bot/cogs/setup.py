"""
Cog exposing slash commands for server setup, AI filter options, and word-list/domain management.
All commands require appropriate server admin/moderator permissions and respond in clear Arabic.
"""

from __future__ import annotations

import io
import json

import discord
from discord import app_commands
from discord.ext import commands

from config.auto_mod import VALID_LEVELS, apply_preset
from config.db_config import ConfigStore


class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot, store: ConfigStore):
        self.bot = bot
        self.store = store

    filter_group = app_commands.Group(name="filter", description="إدارة قائمة الكلمات المحظورة والنطاقات")
    config_group = app_commands.Group(name="config", description="إعدادات وتكاوين البوت")

    @app_commands.command(name="setup", description="إعداد البوت لأول مرة في هذا السيرفر")
    @app_commands.describe(
        log_channel="القناة التي سيتم إرسال سجلات الإشراف إليها",
        mute_role="رتبة الكتم (اختياري، سيتم إنشاء واحدة تلقائيًا إن لم تُحدد)",
        warn_threshold="عدد التحذيرات قبل الكتم التلقائي (افتراضي 3)",
        mute_minutes="مدة الكتم بالدقائق (افتراضي 30)",
        level="مستوى الإشراف التلقائي: low / medium / high",
    )
    @app_commands.choices(
        level=[
            app_commands.Choice(name="منخفض (low)", value="low"),
            app_commands.Choice(name="متوسط (medium)", value="medium"),
            app_commands.Choice(name="مرتفع (high)", value="high"),
        ]
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_command(
        self,
        interaction: discord.Interaction,
        log_channel: discord.TextChannel,
        mute_role: discord.Role | None = None,
        warn_threshold: int | None = None,
        mute_minutes: int | None = None,
        level: app_commands.Choice[str] | None = None,
    ):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        cfg.log_channel_id = log_channel.id
        if mute_role:
            cfg.mute_role_id = mute_role.id

        chosen_level = level.value if level else "medium"
        apply_preset(cfg, chosen_level)

        if warn_threshold:
            cfg.warn_threshold_mute = warn_threshold
        if mute_minutes:
            cfg.mute_duration_minutes = mute_minutes

        await self.store.save_config(cfg)

        await interaction.response.send_message(
            "✅ **تم إعداد بوت حارس Pro بنجاح!**\n"
            f"- قناة السجلات: {log_channel.mention}\n"
            f"- رتبة الكتم: {mute_role.mention if mute_role else 'سيتم إنشاؤها تلقائيًا أو استخدام Timeout'}\n"
            f"- مستوى الإشراف: **{cfg.auto_mod_level}**\n"
            f"- فلتر الذكاء الاصطناعي: {'مفعّل ✅' if cfg.ai_filter_enabled else 'معطّل ❌'}\n"
            f"- عدد التحذيرات قبل الكتم: {cfg.warn_threshold_mute}\n"
            f"- مدة الكتم: {cfg.mute_duration_minutes} دقيقة\n"
            f"- فلتر السبام: {'مفعّل' if cfg.spam_filter_enabled else 'معطّل'}\n"
            f"- حماية من الهجمات: {'مفعّلة' if cfg.raid_protection_enabled else 'معطّلة'}\n\n"
            "يمكنك تعديل الإعدادات في أي وقت عبر `/config show` أو `/setup_ai`.",
            ephemeral=True,
        )

    @app_commands.command(name="setup_ai", description="ضبط إعدادات تصفية الذكاء الاصطناعي (Hugging Face AI)")
    @app_commands.describe(
        enabled="تفعيل أو تعطيل تصفية المحتوى بالذكاء الاصطناعي",
        confidence_threshold="نسبة الثقة المطلوبة للحذف تلقائيًا (من 0.50 إلى 0.95)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ai_command(
        self,
        interaction: discord.Interaction,
        enabled: bool,
        confidence_threshold: float = 0.80
    ):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        cfg.ai_filter_enabled = enabled
        cfg.ai_confidence_threshold = max(0.50, min(0.95, confidence_threshold))
        await self.store.save_config(cfg)

        state = "مفعّل ✅" if enabled else "معطّل ❌"
        pct = int(cfg.ai_confidence_threshold * 100)
        await interaction.response.send_message(
            f"🤖 **تم تحديث إعدادات الذكاء الاصطناعي:**\n"
            f"• الحالة: {state}\n"
            f"• نسبة الثقة المطلوبة: **{pct}%**",
            ephemeral=True
        )

    @config_group.command(name="show", description="عرض إعدادات البوت الحالية")
    async def config_show(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id)
        log_channel = f"<#{cfg.log_channel_id}>" if cfg.log_channel_id else "غير محدد"
        mute_role = f"<@&{cfg.mute_role_id}>" if cfg.mute_role_id else "تلقائي / Timeout"
        exempt = ", ".join(f"<@&{rid}>" for rid in cfg.exempt_role_ids) or "لا يوجد"

        embed = discord.Embed(title="⚙️ إعدادات حارس Pro الحالية", color=discord.Color.blurple())
        embed.add_field(name="قناة السجلات", value=log_channel, inline=False)
        embed.add_field(name="رتبة الكتم", value=mute_role, inline=False)
        embed.add_field(name="مستوى الإشراف", value=cfg.auto_mod_level, inline=True)
        embed.add_field(
            name="الذكاء الاصطناعي (Layer 2)",
            value=f"مفعّل ({int(cfg.ai_confidence_threshold * 100)}%) ✅" if cfg.ai_filter_enabled else "معطّل ❌",
            inline=True,
        )
        embed.add_field(
            name="Timeout الأصلي",
            value="مفعّل ✅" if cfg.use_native_timeout else "معطّل (رتبة فقط)",
            inline=True,
        )
        embed.add_field(
            name="فلتر الألفاظ",
            value="مفعّل ✅" if cfg.profanity_filter_enabled else "معطّل ❌",
            inline=True,
        )
        embed.add_field(
            name="فلتر الروابط",
            value="مفعّل ✅" if cfg.scam_filter_enabled else "معطّل ❌",
            inline=True,
        )
        embed.add_field(
            name="فلتر السبام",
            value="مفعّل ✅" if cfg.spam_filter_enabled else "معطّل ❌",
            inline=True,
        )
        embed.add_field(
            name="حماية الهجمات",
            value="مفعّلة ✅" if cfg.raid_protection_enabled else "معطّلة ❌",
            inline=True,
        )
        embed.add_field(name="حد التحذيرات", value=str(cfg.warn_threshold_mute), inline=True)
        embed.add_field(name="مدة الكتم (دقائق)", value=str(cfg.mute_duration_minutes), inline=True)
        embed.add_field(
            name="حد السبام",
            value=f"{cfg.spam_max_messages} رسالة / {cfg.spam_window_seconds}ث",
            inline=True,
        )
        embed.add_field(
            name="حد الهجوم",
            value=f"{cfg.raid_join_threshold} عضو / {cfg.raid_window_seconds}ث",
            inline=True,
        )
        embed.add_field(
            name="إغلاق تلقائي عند الهجوم",
            value="نعم ✅" if cfg.raid_auto_lockdown else "لا ❌",
            inline=True,
        )
        embed.add_field(name="رتب معفاة", value=exempt, inline=False)
        embed.add_field(name="كلمات مخصصة", value=str(len(cfg.custom_bad_words)), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="set-level", description="تغيير مستوى الإشراف التلقائي")
    @app_commands.describe(level="low = lenient, medium = balanced, high = strict")
    @app_commands.choices(
        level=[
            app_commands.Choice(name="منخفض (low)", value="low"),
            app_commands.Choice(name="متوسط (medium)", value="medium"),
            app_commands.Choice(name="مرتفع (high)", value="high"),
        ]
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_level(self, interaction: discord.Interaction, level: app_commands.Choice[str]):
        if level.value not in VALID_LEVELS:
            await interaction.response.send_message("مستوى غير صالح.", ephemeral=True)
            return
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        apply_preset(cfg, level.value)
        await self.store.save_config(cfg)
        await interaction.response.send_message(
            f"✅ تم ضبط مستوى الإشراف على **{level.value}**.\n"
            f"- تحذيرات قبل الكتم: {cfg.warn_threshold_mute}\n"
            f"- مدة الكتم: {cfg.mute_duration_minutes} دقيقة\n"
            f"- سبام: {cfg.spam_max_messages} رسالة / {cfg.spam_window_seconds}ث\n"
            f"- هجوم: {cfg.raid_join_threshold} عضو / {cfg.raid_window_seconds}ث",
            ephemeral=True,
        )

    @config_group.command(name="set-language", description="تغيير لغة البوت والسيرفر (العربية / English)")
    @app_commands.describe(lang="اختيار لغة البوت (ar = العربية, en = English)")
    @app_commands.choices(
        lang=[
            app_commands.Choice(name="العربية (Arabic)", value="ar"),
            app_commands.Choice(name="English", value="en"),
        ]
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_language(self, interaction: discord.Interaction, lang: app_commands.Choice[str]):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        cfg.language = lang.value
        await self.store.save_config(cfg)
        msg = "✅ تم تغيير لغة السيرفر إلى: **العربية**" if lang.value == "ar" else "✅ Server language updated to: **English**"
        await interaction.response.send_message(msg, ephemeral=True)

    @config_group.command(name="toggle-profanity", description="تفعيل/تعطيل فلتر الألفاظ")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_profanity(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        cfg.profanity_filter_enabled = not cfg.profanity_filter_enabled
        await self.store.save_config(cfg)
        state = "مفعّل ✅" if cfg.profanity_filter_enabled else "معطّل ❌"
        await interaction.response.send_message(f"فلتر الألفاظ الآن: {state}", ephemeral=True)

    @config_group.command(name="toggle-scam", description="تفعيل/تعطيل فلتر الروابط الاحتيالية")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_scam(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        cfg.scam_filter_enabled = not cfg.scam_filter_enabled
        await self.store.save_config(cfg)
        state = "مفعّل ✅" if cfg.scam_filter_enabled else "معطّل ❌"
        await interaction.response.send_message(
            f"فلتر الروابط الاحتيالية الآن: {state}", ephemeral=True
        )

    @config_group.command(name="toggle-spam", description="تفعيل/تعطيل فلتر السبام")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_spam(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        cfg.spam_filter_enabled = not cfg.spam_filter_enabled
        await self.store.save_config(cfg)
        state = "مفعّل ✅" if cfg.spam_filter_enabled else "معطّل ❌"
        await interaction.response.send_message(f"فلتر السبام الآن: {state}", ephemeral=True)

    @config_group.command(name="toggle-raid", description="تفعيل/تعطيل حماية الهجمات")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_raid(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        cfg.raid_protection_enabled = not cfg.raid_protection_enabled
        await self.store.save_config(cfg)
        state = "مفعّلة ✅" if cfg.raid_protection_enabled else "معطّلة ❌"
        await interaction.response.send_message(f"حماية الهجمات الآن: {state}", ephemeral=True)

    @config_group.command(
        name="toggle-lockdown", description="تفعيل/تعطيل الإغلاق التلقائي عند الهجوم"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_lockdown(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        cfg.raid_auto_lockdown = not cfg.raid_auto_lockdown
        await self.store.save_config(cfg)
        state = "مفعّل ✅" if cfg.raid_auto_lockdown else "معطّل ❌"
        await interaction.response.send_message(
            f"الإغلاق التلقائي عند الهجوم: {state}", ephemeral=True
        )

    @config_group.command(name="ignore-channel", description="تجاهل قناة معينة من الفحص")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ignore_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        if channel.id not in cfg.ignored_channel_ids:
            cfg.ignored_channel_ids.append(channel.id)
            await self.store.save_config(cfg)
        await interaction.response.send_message(
            f"تم تجاهل {channel.mention} من الفحص. ✅", ephemeral=True
        )

    @config_group.command(name="exempt-role", description="إضافة رتبة معفاة من الإشراف التلقائي")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def exempt_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.store.add_exempt_role(interaction.guild_id, role.id)
        await interaction.response.send_message(
            f"تمت إضافة {role.mention} إلى الرتب المعفاة. ✅", ephemeral=True
        )

    @config_group.command(name="unexempt-role", description="إزالة رتبة من الإعفاء")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def unexempt_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.store.remove_exempt_role(interaction.guild_id, role.id)
        await interaction.response.send_message(
            f"تمت إزالة {role.mention} من الرتب المعفاة. ✅", ephemeral=True
        )

    @config_group.command(name="export", description="تصدير إعدادات أمان السيرفر في ملف JSON للاحتفاظ بنسخة احتياطية")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def export_config(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
        data = cfg.to_dict()
        buffer = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        file = discord.File(fp=buffer, filename=f"haris_config_{interaction.guild_id}.json")
        await interaction.response.send_message(
            "📦 **تم تصدير إعدادات أمان السيرفر بنجاح:**", file=file, ephemeral=True
        )

    @config_group.command(name="import", description="استيراد إعدادات أمان السيرفر من ملف JSON")
    @app_commands.describe(file="ملف إعدادات JSON المصدّر سابقًا")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def import_config(self, interaction: discord.Interaction, file: discord.Attachment):
        if not file.filename.endswith(".json"):
            await interaction.response.send_message("❌ **خطأ:** يجب رفع ملف بصيغة `.json` فقط.", ephemeral=True)
            return

        try:
            content = await file.read()
            data = json.loads(content.decode("utf-8"))
            cfg = await self.store.get_config(interaction.guild_id, use_cache=False)
            
            # Apply imported fields safely
            for key, val in data.items():
                if hasattr(cfg, key) and key not in ("guild_id", "stats_deleted_messages", "stats_warn_count", "stats_mute_count"):
                    setattr(cfg, key, val)

            await self.store.save_config(cfg)
            await self._invalidate_moderation_cog_filters(interaction.guild_id)
            await interaction.response.send_message("✅ **تم استيراد وتطبيق إعدادات الأمان بنجاح!**", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **فشل استيراد الملف:** {e}", ephemeral=True)

    @filter_group.command(name="add-word", description="إضافة كلمة إلى قائمة الكلمات المحظورة")
    @app_commands.describe(word="الكلمة المراد إضافتها")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def add_word(self, interaction: discord.Interaction, word: str):
        await self.store.add_custom_word(interaction.guild_id, word)
        await self._invalidate_moderation_cog_filters(interaction.guild_id)
        await interaction.response.send_message("تمت إضافة الكلمة إلى الفلتر. ✅", ephemeral=True)

    @filter_group.command(name="remove-word", description="إزالة كلمة من قائمة الكلمات المحظورة")
    @app_commands.describe(word="الكلمة المراد إزالتها")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove_word(self, interaction: discord.Interaction, word: str):
        await self.store.remove_custom_word(interaction.guild_id, word)
        await self._invalidate_moderation_cog_filters(interaction.guild_id)
        await interaction.response.send_message("تمت إزالة الكلمة من الفلتر. ✅", ephemeral=True)

    @filter_group.command(name="list-words", description="عرض الكلمات المخصصة المضافة في هذا السيرفر")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def list_words(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id)
        if not cfg.custom_bad_words:
            await interaction.response.send_message(
                "لا توجد كلمات مخصصة مضافة بعد.", ephemeral=True
            )
            return
        words_list = "\n".join(f"- {w}" for w in cfg.custom_bad_words)
        await interaction.response.send_message(
            f"**الكلمات المخصصة:**\n{words_list}", ephemeral=True
        )

    @filter_group.command(
        name="whitelist-domain", description="إضافة نطاق موثوق لاستثنائه من فلتر الروابط"
    )
    @app_commands.describe(domain="اسم النطاق، مثل example.com")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def whitelist_domain(self, interaction: discord.Interaction, domain: str):
        await self.store.add_whitelisted_domain(interaction.guild_id, domain)
        await self._invalidate_moderation_cog_filters(interaction.guild_id)
        await interaction.response.send_message(
            f"تمت إضافة `{domain.strip().lower()}` إلى النطاقات الموثوقة. ✅", ephemeral=True
        )

    @filter_group.command(
        name="remove-domain", description="إزالة نطاق من القائمة الموثوقة لفلتر الروابط"
    )
    @app_commands.describe(domain="اسم النطاق، مثل example.com")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove_domain(self, interaction: discord.Interaction, domain: str):
        await self.store.remove_whitelisted_domain(interaction.guild_id, domain)
        await self._invalidate_moderation_cog_filters(interaction.guild_id)
        await interaction.response.send_message(
            f"تمت إزالة `{domain.strip().lower()}` من النطاقات الموثوقة. ✅", ephemeral=True
        )

    async def _invalidate_moderation_cog_filters(self, guild_id: int) -> None:
        mod_cog = self.bot.get_cog("ModerationCog")
        if mod_cog:
            await mod_cog.invalidate_filters(guild_id)


async def setup(bot: commands.Bot):
    store: ConfigStore = bot.config_store
    await bot.add_cog(SetupCog(bot, store))
