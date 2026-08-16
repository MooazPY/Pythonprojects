"""Unit tests for HarisBot global slash command error handler."""

import asyncio
from unittest.mock import AsyncMock, MagicMock
import discord
from discord import app_commands
from main import HarisBot


def _make_mock_interaction(is_done=False):
    interaction = AsyncMock(spec=discord.Interaction)
    interaction.response.is_done.return_value = is_done
    interaction.response.send_message = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction


def test_missing_permissions_error():
    async def _run():
        bot = HarisBot()
        interaction = _make_mock_interaction(is_done=False)

        err = app_commands.MissingPermissions(["manage_messages"])
        await bot.on_tree_error(interaction, err)

        interaction.response.send_message.assert_called_once()
        args, kwargs = interaction.response.send_message.call_args
        assert "ليس لديك الصلاحية الكافية" in args[0]
        assert kwargs.get("ephemeral") is True

    asyncio.run(_run())


def test_missing_role_error():
    async def _run():
        bot = HarisBot()
        interaction = _make_mock_interaction(is_done=False)

        err = app_commands.MissingRole("Moderator")
        await bot.on_tree_error(interaction, err)

        interaction.response.send_message.assert_called_once()
        args, kwargs = interaction.response.send_message.call_args
        assert "Moderator" in args[0]
        assert kwargs.get("ephemeral") is True

    asyncio.run(_run())


def test_cooldown_error():
    async def _run():
        bot = HarisBot()
        interaction = _make_mock_interaction(is_done=False)

        err = app_commands.CommandOnCooldown(cooldown=MagicMock(), retry_after=5.4)
        await bot.on_tree_error(interaction, err)

        interaction.response.send_message.assert_called_once()
        args, kwargs = interaction.response.send_message.call_args
        assert "الأمر قيد الانتظار" in args[0]
        assert "5.4" in args[0]
        assert kwargs.get("ephemeral") is True

    asyncio.run(_run())


def test_check_failure_error():
    async def _run():
        bot = HarisBot()
        interaction = _make_mock_interaction(is_done=False)

        err = app_commands.CheckFailure()
        await bot.on_tree_error(interaction, err)

        interaction.response.send_message.assert_called_once()
        args, kwargs = interaction.response.send_message.call_args
        assert "لا تملك الصلاحيات" in args[0]
        assert kwargs.get("ephemeral") is True

    asyncio.run(_run())


def test_generic_unexpected_error():
    async def _run():
        bot = HarisBot()
        interaction = _make_mock_interaction(is_done=False)
        interaction.command.name = "test_cmd"

        err = app_commands.AppCommandError("Unexpected failure")
        await bot.on_tree_error(interaction, err)

        interaction.response.send_message.assert_called_once()
        args, kwargs = interaction.response.send_message.call_args
        assert "خطأ غير متوقع" in args[0]
        assert kwargs.get("ephemeral") is True

    asyncio.run(_run())


def test_error_handler_pre_acknowledged_followup():
    async def _run():
        bot = HarisBot()
        interaction = _make_mock_interaction(is_done=True)

        err = app_commands.MissingPermissions(["manage_guild"])
        await bot.on_tree_error(interaction, err)

        interaction.followup.send.assert_called_once()
        args, kwargs = interaction.followup.send.call_args
        assert "ليس لديك الصلاحية" in args[0]
        assert kwargs.get("ephemeral") is True

    asyncio.run(_run())

