"""
Moderation action logic: applying warnings, mutes, incident logging, and stats tracking.
Independent of discord.py Cog wiring for full modularity and unit-testing ease.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import logging
import time
from typing import Optional

import discord

from config.db_config import ConfigStore, GuildConfig

logger = logging.getLogger("arabic_mod_bot.moderation")

MUTE_ROLE_NAME = "مكتوم"


def is_member_exempt(member: discord.Member, cfg: GuildConfig) -> bool:
    if member.guild_permissions.manage_messages or member.guild_permissions.administrator:
        return True
    member_role_ids = {role.id for role in member.roles}
    return bool(member_role_ids.intersection(cfg.exempt_role_ids))


async def get_or_create_mute_role(guild: discord.Guild, cfg: GuildConfig) -> Optional[discord.Role]:
    if cfg.mute_role_id:
        role = guild.get_role(cfg.mute_role_id)
        if role:
            return role

    role = discord.utils.get(guild.roles, name=MUTE_ROLE_NAME)
    if role:
        return role

    try:
        role = await guild.create_role(
            name=MUTE_ROLE_NAME,
            reason="إنشاء رتبة الكتم تلقائيًا لبوت الإشراف حارس",
        )
        for channel in guild.channels:
            try:
                await channel.set_permissions(
                    role, send_messages=False, add_reactions=False, speak=False
                )
            except discord.Forbidden:
                continue
        return role
    except discord.Forbidden:
        logger.warning("Missing permission to create mute role in guild %s", guild.id)
        return None


async def log_incident(
    bot: discord.Client,
    cfg: GuildConfig,
    *,
    title: str,
    member: discord.Member,
    reason: str,
    extra: Optional[str] = None,
    color: discord.Color = discord.Color.orange(),
) -> None:
    if not cfg.log_channel_id:
        return

    channel = bot.get_channel(cfg.log_channel_id)
    if channel is None:
        return

    embed = discord.Embed(title=title, color=color, timestamp=dt.datetime.now(dt.timezone.utc))
    embed.add_field(name="👤 العضو", value=f"{member.mention} (`{member.id}`)", inline=True)
    embed.add_field(name="📝 السبب", value=reason, inline=False)
    if extra:
        embed.add_field(name="ℹ️ تفاصيل إضافية", value=extra, inline=False)
    embed.set_footer(text="حارس — بوت الإشراف الذكي Pro")

    try:
        await channel.send(embed=embed)
    except discord.Forbidden:
        logger.warning("Missing permission to post in log channel for guild %s", cfg.guild_id)


async def warn_member(
    bot: discord.Client,
    store: ConfigStore,
    cfg: GuildConfig,
    member: discord.Member,
    reason: str,
    moderator_id: int,
) -> int:
    count = await store.add_warning(cfg.guild_id, member.id, reason, moderator_id)

    await log_incident(
        bot,
        cfg,
        title="⚠️ تحذير جديد",
        member=member,
        reason=reason,
        extra=f"عدد التحذيرات الحالي: **{count}/{cfg.warn_threshold_mute}**",
    )

    if count >= cfg.warn_threshold_mute:
        await mute_member(
            bot,
            store,
            cfg,
            member,
            reason=f"تجاوز الحد المسموح من التحذيرات ({count}/{cfg.warn_threshold_mute})",
            duration_minutes=cfg.mute_duration_minutes,
        )

    return count


async def _apply_role_mute(
    member: discord.Member, cfg: GuildConfig, reason: str
) -> tuple[bool, Optional[discord.Role]]:
    role = await get_or_create_mute_role(member.guild, cfg)
    if role is None:
        return False, None
    try:
        await member.add_roles(role, reason=reason)
    except discord.Forbidden:
        logger.warning("Missing permission to mute member %s in guild %s", member.id, cfg.guild_id)
        return False, None
    return True, role


async def _apply_timeout_mute(
    member: discord.Member, reason: str, duration_minutes: int
) -> bool:
    if not member.guild.me.guild_permissions.moderate_members:
        return False
    until = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=duration_minutes)
    try:
        await member.timeout(until, reason=reason)
        return True
    except discord.Forbidden:
        logger.warning(
            "Missing permission to timeout member %s in guild %s", member.id, member.guild.id
        )
        return False


async def unmute_member(
    bot: discord.Client,
    store: ConfigStore,
    guild: discord.Guild,
    user_id: int,
    *,
    mute_method: str,
    role_id: Optional[int],
    reason: str = "انتهاء مدة الكتم",
) -> None:
    member = guild.get_member(user_id)
    if member is None:
        try:
            member = await guild.fetch_member(user_id)
        except discord.NotFound:
            await store.cancel_unmute(guild.id, user_id)
            return

    try:
        if mute_method == "timeout" and member.timed_out_until:
            await member.timeout(None, reason=reason)
        elif mute_method == "role" and role_id:
            role = guild.get_role(role_id)
            if role and role in member.roles:
                await member.remove_roles(role, reason=reason)
    except discord.HTTPException as exc:
        logger.warning("Failed to unmute %s in guild %s: %s", user_id, guild.id, exc)
    finally:
        await store.cancel_unmute(guild.id, user_id)


async def mute_member(
    bot: discord.Client,
    store: ConfigStore,
    cfg: GuildConfig,
    member: discord.Member,
    reason: str,
    duration_minutes: int,
) -> bool:
    mute_method = "role"
    role_id: Optional[int] = None
    success = False

    if cfg.use_native_timeout:
        success = await _apply_timeout_mute(member, reason, duration_minutes)
        if success:
            mute_method = "timeout"

    if not success:
        success, role = await _apply_role_mute(member, cfg, reason)
        if success and role:
            mute_method = "role"
            role_id = role.id

    if not success:
        return False

    unmute_at = time.time() + duration_minutes * 60
    await store.schedule_unmute(
        cfg.guild_id,
        member.id,
        unmute_at,
        mute_method,
        role_id=role_id,
        reason=reason,
    )

    await log_incident(
        bot,
        cfg,
        title="🔇 تم تطبيق الكتم التلقائي",
        member=member,
        reason=reason,
        extra=f"المدة: **{duration_minutes} دقيقة** | الطريقة: `{mute_method}`",
        color=discord.Color.red(),
    )

    delay = max(0.0, unmute_at - time.time())
    bot.loop.create_task(
        _unmute_after_delay(bot, store, cfg.guild_id, member.id, mute_method, role_id, delay)
    )
    return True


async def _unmute_after_delay(
    bot: discord.Client,
    store: ConfigStore,
    guild_id: int,
    user_id: int,
    mute_method: str,
    role_id: Optional[int],
    delay: float,
) -> None:
    await asyncio.sleep(delay)
    guild = bot.get_guild(guild_id)
    if guild is None:
        return
    await unmute_member(
        bot, store, guild, user_id, mute_method=mute_method, role_id=role_id
    )


async def restore_pending_unmutes(bot: discord.Client, store: ConfigStore) -> None:
    pending = await store.get_pending_unmutes()
    now = time.time()
    for entry in pending:
        guild = bot.get_guild(entry.guild_id)
        if guild is None:
            continue
        delay = max(0.0, entry.unmute_at - now)
        if delay == 0:
            await unmute_member(
                bot,
                store,
                guild,
                entry.user_id,
                mute_method=entry.mute_method,
                role_id=entry.role_id,
            )
        else:
            bot.loop.create_task(
                _unmute_after_delay(
                    bot,
                    store,
                    entry.guild_id,
                    entry.user_id,
                    entry.mute_method,
                    entry.role_id,
                    delay,
                )
            )
    logger.info("Restored %d pending unmute(s) from SQLite storage.", len(pending))


async def delete_and_flag(
    bot: discord.Client,
    store: ConfigStore,
    cfg: GuildConfig,
    message: discord.Message,
    reason: str,
    moderator_id: int,
) -> None:
    try:
        await message.delete()
        await store.increment_stat(cfg.guild_id, "deleted_messages", 1)
    except discord.Forbidden:
        logger.warning("Missing permission to delete message in guild %s", cfg.guild_id)
    except discord.NotFound:
        pass

    if isinstance(message.author, discord.Member):
        await warn_member(bot, store, cfg, message.author, reason, moderator_id)
