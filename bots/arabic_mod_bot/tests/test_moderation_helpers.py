"""Unit tests for moderation helper logic."""

from unittest.mock import MagicMock

from config.db_config import GuildConfig
from moderation import is_member_exempt


def _member(*, manage_messages=False, administrator=False, role_ids=None):
    member = MagicMock()
    perms = MagicMock()
    perms.manage_messages = manage_messages
    perms.administrator = administrator
    member.guild_permissions = perms
    roles = []
    for rid in role_ids or []:
        role = MagicMock()
        role.id = rid
        roles.append(role)
    member.roles = roles
    return member


def test_admin_is_exempt():
    cfg = GuildConfig(guild_id=1)
    assert is_member_exempt(_member(administrator=True), cfg)


def test_exempt_role_is_exempt():
    cfg = GuildConfig(guild_id=1, exempt_role_ids=[999])
    assert is_member_exempt(_member(role_ids=[999]), cfg)


def test_regular_member_not_exempt():
    cfg = GuildConfig(guild_id=1)
    assert not is_member_exempt(_member(), cfg)
