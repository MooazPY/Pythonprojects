"""Unit tests for scam link detection."""

from filters.scam_links import ScamLinkDetector


def test_blocks_blacklisted_domain():
    detector = ScamLinkDetector()
    result = detector.check("check this https://dlscord.com/nitro")
    assert result.is_scam
    assert "dlscord.com" in result.matched_domains


def test_allows_discord_gg():
    detector = ScamLinkDetector()
    result = detector.check("join us https://discord.gg/example")
    assert not result.is_scam


def test_detects_scam_phrase_with_link():
    detector = ScamLinkDetector()
    result = detector.check("free nitro https://evil-site.xyz/claim")
    assert result.is_scam


def test_guild_whitelist():
    detector = ScamLinkDetector()
    detector.set_guild_whitelist(["mycdn.com"])
    result = detector.check("see https://mycdn.com/file")
    assert not result.is_scam


def test_suspicious_tld_keyword():
    detector = ScamLinkDetector()
    result = detector.check("https://discord-nitro-free.tk")
    assert result.is_scam
