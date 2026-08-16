"""
Cog that listens to messages, executes multi-layer moderation filters (including Hugging Face AI),
and provides moderation commands and diagnostic tools.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

import discord
from discord import app_commands
from discord.ext import tasks, commands

from config.db_config import ConfigStore
from filters.arabic_words import DEFAULT_BAD_WORDS, ArabicWordFilter, normalize_arabic
from filters.hf_ai_classifier import HuggingFaceClassifier
from filters.raid_protection import RaidTracker
from filters.scam_links import ScamLinkDetector
from filters.spam_detection import SpamTracker
from moderation import delete_and_flag, is_member_exempt, log_incident, warn_member

logger = logging.getLogger("arabic_mod_bot.cogs.moderation")


def generate_visual_bar(value: int, max_val: int = 100, length: int = 10) -> str:
    max_v = max(max_val, value, 1)
    filled = min(length, max(0, int((value / max_v) * length)))
    return "█" * filled + "░" * (length - filled)


class AppealModal(discord.ui.Modal, title="تقديم طلب اعتراض / Submit Appeal"):
    reason_input = discord.ui.TextInput(
        label="سبب الاعتراض / Appeal Reason",
        style=discord.TextStyle.paragraph,
        placeholder="اشرح سبب طلبك لإلغاء الإجراء الإداري...",
        required=True,
        max_length=1000,
    )

    def __init__(self, bot: commands.Bot, store: ConfigStore):
        super().__init__()
        self.bot = bot
        self.store = store

    async def on_submit(self, interaction: discord.Interaction):
        cfg = await self.store.get_config(interaction.guild_id)
        reason = self.reason_input.value

        embed = discord.Embed(
            title="📝 طلب اعتراض جديد / New Appeal Received",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="العضو / User", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
        embed.add_field(name="السبب / Reason", value=reason, inline=False)
        embed.set_footer(text="Haris Pro Appeals System")

        view = PersistentAppealView(store=self.store, user_id=interaction.user.id)

        log_channel = None
        if cfg.log_channel_id:
            log_channel = interaction.guild.get_channel(cfg.log_channel_id)
        if not log_channel:
            log_channel = discord.utils.get(interaction.guild.text_channels, name="حارس-الإشراف")

        if log_channel:
            await log_channel.send(embed=embed, view=view)
            msg = "✅ **تم تقديم طلب الاعتراض بنجاح.** سيتم مراجعته من قبل إدارة السيرفر." if cfg.language == "ar" else "✅ **Appeal submitted successfully.** Moderators will review your request."
        else:
            msg = "❌ **خطأ:** قناة الإشراف غير معينة."

        await interaction.response.send_message(msg, ephemeral=True)


class PersistentAppealView(discord.ui.View):
    def __init__(self, store: ConfigStore, user_id: Optional[int] = None):
        super().__init__(timeout=None)
        self.store = store

    def _extract_user_id(self, interaction: discord.Interaction) -> Optional[int]:
        if interaction.message and interaction.message.embeds:
            embed = interaction.message.embeds[0]
            for field in embed.fields:
                if field.name and ("User" in field.name or "العضو" in field.name):
                    import re
                    match = re.search(r"`(\d+)`", field.value)
                    if match:
                        return int(match.group(1))
        return None

    @discord.ui.button(label="قبول الاعتراض (Approve)", style=discord.ButtonStyle.success, custom_id="appeal_accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ ليس لديك صلاحية اتخاذ هذا القرار.", ephemeral=True)
            return

        target_user_id = self._extract_user_id(interaction)
        if target_user_id:
            new_count = await self.store.decrement_warning(interaction.guild_id, target_user_id, 1)
            msg_target = f"<@{target_user_id}> (المتبقي: {new_count} تحذير)"
        else:
            msg_target = "العضو"

        button.disabled = True
        self.children[1].disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"✅ تم قبول طلب الاعتراض لـ {msg_target} وخصم تحذير واحد.", ephemeral=False)

    @discord.ui.button(label="رفض الاعتراض (Reject)", style=discord.ButtonStyle.danger, custom_id="appeal_reject")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ ليس لديك صلاحية اتخاذ هذا القرار.", ephemeral=True)
            return

        target_user_id = self._extract_user_id(interaction)
        msg_target = f"<@{target_user_id}>" if target_user_id else "العضو"

        button.disabled = True
        self.children[0].disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"❌ تم رفض طلب الاعتراض لـ {msg_target}.", ephemeral=False)


# Alias for backward compatibility
AppealView = PersistentAppealView


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot, store: ConfigStore):
        self.bot = bot
        self.store = store
        self._word_filters: Dict[int, ArabicWordFilter] = {}
        self._scam_detectors: Dict[int, ScamLinkDetector] = {}
        self._ai_classifier = HuggingFaceClassifier()
        self._spam_tracker = SpamTracker()
        self._raid_tracker = RaidTracker()
        self.cleanup_spam_history_task.start()

    def cog_unload(self):
        self.cleanup_spam_history_task.cancel()

    @tasks.loop(minutes=10)
    async def cleanup_spam_history_task(self):
        cleaned = self._spam_tracker.cleanup_stale_history(max_age_seconds=600)
        if cleaned > 0:
            logger.debug("Cleaned %d stale user entries from SpamTracker history.", cleaned)

    async def _get_word_filter(self, guild_id: int) -> ArabicWordFilter:
        cfg = await self.store.get_config(guild_id)
        if guild_id not in self._word_filters:
            self._word_filters[guild_id] = ArabicWordFilter(DEFAULT_BAD_WORDS, cfg.custom_bad_words)
        else:
            self._word_filters[guild_id].set_custom_words(cfg.custom_bad_words)
        return self._word_filters[guild_id]

    async def _get_scam_detector(self, guild_id: int) -> ScamLinkDetector:
        cfg = await self.store.get_config(guild_id)
        if guild_id not in self._scam_detectors:
            self._scam_detectors[guild_id] = ScamLinkDetector()
        self._scam_detectors[guild_id].set_guild_whitelist(cfg.whitelisted_domains)
        return self._scam_detectors[guild_id]

    async def invalidate_filters(self, guild_id: int) -> None:
        await self.store.invalidate(guild_id)

    async def _notify_violation(
        self, channel: discord.TextChannel, member: discord.Member, message: str
    ) -> None:
        try:
            await channel.send(f"{member.mention} {message}", delete_after=10)
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        cfg = await self.store.get_config(message.guild.id)

        if message.channel.id in cfg.ignored_channel_ids:
            return

        if not isinstance(message.author, discord.Member):
            return

        if is_member_exempt(message.author, cfg):
            return

        # Layer 1: Arabic Dictionary & Pattern Filter
        if cfg.profanity_filter_enabled:
            word_filter = await self._get_word_filter(message.guild.id)
            hits = word_filter.check(message.content)
            if hits:
                await delete_and_flag(
                    self.bot,
                    self.store,
                    cfg,
                    message,
                    reason=f"استخدام لغة غير لائقة (فلتر الكلمات: {', '.join(hits)})",
                    moderator_id=self.bot.user.id,
                )
                await self._notify_violation(
                    message.channel,
                    message.author,
                    "تم حذف رسالتك لاحتوائها على لغة غير لائقة ⚠️",
                )
                return

        # Layer 2: Hugging Face AI Toxicity & Hate Speech Classifier
        if cfg.ai_filter_enabled:
            ai_result = await self._ai_classifier.classify_text(
                message.content, confidence_threshold=cfg.ai_confidence_threshold
            )
            if ai_result.is_toxic:
                score_pct = int(ai_result.confidence * 100)
                await delete_and_flag(
                    self.bot,
                    self.store,
                    cfg,
                    message,
                    reason=f"محتوى مسيء تم اكتشافه بواسطة الذكاء الاصطناعي (نسبة الثقة: {score_pct}%)",
                    moderator_id=self.bot.user.id,
                )
                await self._notify_violation(
                    message.channel,
                    message.author,
                    "تم حذف رسالتك تلقائيًا بواسطة نظام الذكاء الاصطناعي لاحتوائها على محتوى مسيء 🤖⚠️",
                )
                return

        # Layer 3: Scam Links & Phishing Filter
        if cfg.scam_filter_enabled:
            scam_detector = await self._get_scam_detector(message.guild.id)
            result = scam_detector.check(message.content)
            if result.is_scam:
                await delete_and_flag(
                    self.bot,
                    self.store,
                    cfg,
                    message,
                    reason=f"رابط احتيالي مشتبه به ({', '.join(result.reasons)})",
                    moderator_id=self.bot.user.id,
                )
                await self._notify_violation(
                    message.channel,
                    message.author,
                    "تم حذف رسالتك لاحتوائها على رابط مشتبه به (احتيال) 🚫",
                )
                return

        # Layer 4: Spam Detection Filter
        if cfg.spam_filter_enabled:
            spam_result = self._spam_tracker.check(
                message.guild.id,
                message.author.id,
                message.content,
                max_messages=cfg.spam_max_messages,
                window_seconds=cfg.spam_window_seconds,
            )
            if spam_result.is_spam:
                await delete_and_flag(
                    self.bot,
                    self.store,
                    cfg,
                    message,
                    reason=f"رسائل مزعجة / سبام ({spam_result.reason})",
                    moderator_id=self.bot.user.id,
                )
                await self._notify_violation(
                    message.channel,
                    message.author,
                    "تم حذف رسالتك بسبب إرسال رسائل متكررة أو سبام ⚠️",
                )
                self._spam_tracker.clear_user(message.guild.id, message.author.id)
                return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = await self.store.get_config(member.guild.id)
        if not cfg.raid_protection_enabled:
            return

        self._raid_tracker.record_join(member.guild.id, cfg.raid_window_seconds)
        raid = self._raid_tracker.check_threshold(
            member.guild.id, cfg.raid_join_threshold, cfg.raid_window_seconds
        )
        if not raid.is_raid:
            return

        await log_incident(
            self.bot,
            cfg,
            title="🚨 تنبيه: هجوم محتمل (Raid)",
            member=member,
            reason="عدد كبير من الأعضاء انضموا في وقت قصير",
            extra=f"عدد الانضمامات: {raid.join_count} خلال {cfg.raid_window_seconds} ثانية",
            color=discord.Color.dark_red(),
        )

        if cfg.raid_auto_lockdown and not self._raid_tracker.is_lockdown(member.guild.id):
            await self._apply_lockdown(member.guild, cfg)

    async def _apply_lockdown(self, guild: discord.Guild, cfg) -> None:
        if not guild.me.guild_permissions.manage_channels:
            logger.warning("Cannot lock down guild %s — missing Manage Channels.", guild.id)
            return

        everyone = guild.default_role
        locked = 0
        for channel in guild.text_channels:
            try:
                await channel.set_permissions(
                    everyone, send_messages=False, reason="إغلاق تلقائي بسبب هجوم محتمل"
                )
                locked += 1
            except discord.Forbidden:
                continue

        self._raid_tracker.mark_lockdown(guild.id)
        if cfg.log_channel_id:
            log_channel = guild.get_channel(cfg.log_channel_id)
            if log_channel:
                try:
                    await log_channel.send(
                        f"🔒 **تم تفعيل الإغلاق التلقائي** — تم تقييد الكتابة في {locked} قناة."
                    )
                except discord.Forbidden:
                    pass

    @app_commands.command(name="analyze_text", description="تحليل نص عربي ومعاينة نتائج الذكاء الاصطناعي وفلتر الكلمات")
    @app_commands.describe(text="النص المراد تحليله")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def analyze_text_command(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild_id or 0
        cfg = await self.store.get_config(guild_id)

        # 1. Normalization
        normalized = normalize_arabic(text)

        # 2. Dictionary Filter check
        word_filter = await self._get_word_filter(guild_id)
        dict_hits = word_filter.check(text)

        # 3. AI Toxicity Check
        ai_res = await self._ai_classifier.classify_text(
            text, confidence_threshold=cfg.ai_confidence_threshold
        )

        embed = discord.Embed(
            title="🔍 نتيجة تحليل النص الذكي (Haris AI Analytics)",
            color=discord.Color.purple()
        )
        embed.add_field(name="📝 النص الأصلي", value=f"```{text}```", inline=False)
        embed.add_field(name="🔤 النص المعالج (Normalization)", value=f"```{normalized}```", inline=False)
        embed.add_field(
            name="📚 فلتر الكلمات (Layer 1)",
            value=f"✅ نظيف" if not dict_hits else f"⚠️ تم اكتشاف: `{', '.join(dict_hits)}`",
            inline=True
        )

        ai_status = "⚠️ محتوى مسيء" if ai_res.is_toxic else "✅ نظيف / غير مسيء"
        if ai_res.error:
            ai_status += f" (وضع الاحتياطي Local)"
            ai_details = f"**النتيجة:** {ai_status}\n"
            if ai_res.label == "no_token":
                ai_details += "⚠️ **سبب التعطيل:** يتطلب إضافة توكن مجاني `HUGGINGFACE_TOKEN` في ملف `.env` (HTTP 401)"
            else:
                ai_details += f"⚠️ **سبب التعطيل:** `{ai_res.error}`"
        else:
            toxic_pct = int(ai_res.toxic_score * 100)
            conf_pct = int(ai_res.confidence * 100)
            ai_details = f"**النتيجة:** {ai_status}\n"
            ai_details += f"**احتمالية الإساءة:** `{toxic_pct}%`\n"
            ai_details += f"**التصنيف الأصلي:** `{ai_res.label.upper()}` (`{conf_pct}%`)"

        embed.add_field(
            name="🤖 الذكاء الاصطناعي HF (Layer 2)",
            value=ai_details,
            inline=True
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="appeal", description="تقديم طلب اعتراض على تحذير أو كتم إداري")
    async def appeal_command(self, interaction: discord.Interaction):
        modal = AppealModal(self.bot, self.store)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="stats", description="عرض إحصائيات الإشراف والحماية للسيرفر")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def stats_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        cfg = await self.store.get_config(interaction.guild_id)

        max_val = max(cfg.stats_deleted_messages, cfg.stats_warn_count, cfg.stats_mute_count, 10)

        del_bar = generate_visual_bar(cfg.stats_deleted_messages, max_val)
        warn_bar = generate_visual_bar(cfg.stats_warn_count, max_val)
        mute_bar = generate_visual_bar(cfg.stats_mute_count, max_val)

        embed = discord.Embed(
            title="📊 إحصائيات حماية وإشراف حارس Pro",
            color=discord.Color.green()
        )
        embed.add_field(name="🗑️ الرسائل المحذوفة", value=f"**{cfg.stats_deleted_messages}**\n`{del_bar}`", inline=False)
        embed.add_field(name="⚠️ التحذيرات المصدرة", value=f"**{cfg.stats_warn_count}**\n`{warn_bar}`", inline=False)
        embed.add_field(name="🔇 حالات الكتم المنفذة", value=f"**{cfg.stats_mute_count}**\n`{mute_bar}`", inline=False)
        embed.add_field(name="🤖 حالة الذكاء الاصطناعي", value="مفعل ✅" if cfg.ai_filter_enabled else "معطل ❌", inline=True)
        embed.add_field(name="🛡️ مستوى الحماية", value=f"`{cfg.auto_mod_level.upper()}`", inline=True)
        embed.add_field(name="🌐 لغة السيرفر", value=f"`{cfg.language.upper()}`", inline=True)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="unlock", description="إلغاء الإغلاق التلقائي بعد هجوم")
    @app_commands.checks.has_permissions(administrator=True)
    async def unlock_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        everyone = guild.default_role
        restored = 0
        for channel in guild.text_channels:
            try:
                await channel.set_permissions(
                    everyone, send_messages=None, reason="إلغاء الإغلاق بعد الهجوم"
                )
                restored += 1
            except discord.Forbidden:
                continue

        self._raid_tracker.clear_lockdown(guild.id)
        await interaction.followup.send(
            f"✅ تم إلغاء الإغلاق — أُعيدت صلاحيات الكتابة في {restored} قناة."
        )

    warnings_group = app_commands.Group(name="warnings", description="إدارة تحذيرات الأعضاء")

    @warnings_group.command(name="check", description="عرض عدد تحذيرات عضو")
    @app_commands.describe(member="العضو المراد التحقق منه")
    async def warnings_check(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)
        count = await self.store.get_warning_count(interaction.guild_id, member.id)
        await interaction.followup.send(
            f"لدى {member.mention} **{count}** تحذير(ات)."
        )

    @warnings_group.command(name="clear", description="مسح تحذيرات عضو")
    @app_commands.describe(member="العضو المراد مسح تحذيراته")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warnings_clear(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)
        await self.store.clear_warnings(interaction.guild_id, member.id)
        await interaction.followup.send(
            f"تم مسح تحذيرات {member.mention}. ✅"
        )

    @app_commands.command(name="warn", description="توجيه تحذير يدوي لعضو")
    @app_commands.describe(member="العضو", reason="سبب التحذير")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn_command(
        self, interaction: discord.Interaction, member: discord.Member, reason: str
    ):
        await interaction.response.defer(ephemeral=True)
        cfg = await self.store.get_config(interaction.guild_id)

        count = await warn_member(
            self.bot, self.store, cfg, member, reason, interaction.user.id
        )
        await interaction.followup.send(
            f"تم تحذير {member.mention}. إجمالي التحذيرات: {count}"
        )


async def setup(bot: commands.Bot):
    store: ConfigStore = bot.config_store
    await bot.add_cog(ModerationCog(bot, store))