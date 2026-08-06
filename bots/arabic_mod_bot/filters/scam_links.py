"""
Scam link and fake-nitro/crypto-airdrop detection.

Two layers of detection:
  1. Domain blacklist — exact / suffix match against known scam domains
     and known Discord/Steam typosquats.
  2. Heuristic pattern matching — regex over the full message for common
     scam phrasing (free nitro, crypto airdrop/giveaway, urgency + link,
     "steam gift" typosquat patterns) combined with a URL.

This is intentionally conservative about false positives: legitimate
discord.com / discord.gg / steamcommunity.com links are always allowed
via an explicit trusted-domain allowlist that guild-level whitelisting
can extend.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from utils.data_loader import load_scam_domains

_URL_RE = re.compile(r"https?://[^\s<>\"]+|(?<![\w@])(?:www\.)[^\s<>\"]+", re.IGNORECASE)

# Domains that should never be flagged even if they match a heuristic below.
TRUSTED_DOMAINS = {
    "discord.com",
    "discord.gg",
    "discordapp.com",
    "discordstatus.com",
    "steamcommunity.com",
    "steampowered.com",
}

_FALLBACK_DOMAIN_BLACKLIST = {
    "dlscord.com",
    "discrod.com",
    "discordapp.gift",
    "discord-nitro.com",
    "discord-gift.com",
    "discordnitro.gift",
    "discord-airdrop.com",
    "steamcomminuty.com",
    "steamcommumity.com",
    "steamcommunity.ru",
    "steancommunity.com",
    "dlscord-nitro.com",
    "discord.gift-nitro.com",
    "discocd.gift",
}

DOMAIN_BLACKLIST = load_scam_domains(_FALLBACK_DOMAIN_BLACKLIST)

# Suspicious TLD/keyword combinations frequently used for throwaway scam
# domains (e.g. "discord-nitro-free.tk").
_SUSPICIOUS_KEYWORD_RE = re.compile(
    r"(discord|nitro|steam|valorant|crypto|airdrop|giveaway)[-.]?(free|gift|claim|hack|nitro)",
    re.IGNORECASE,
)
_SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".gift"}

# Phrase-level heuristics: common scam message framing in Arabic + English,
# only meaningful when combined with a link (checked separately).
_SCAM_PHRASE_RE = re.compile(
    r"(نيترو\s*مجان|فري\s*نيترو|free\s*nitro|nitro\s*giveaway|"
    r"airdrop|هدية\s*نيترو|اربح\s*.*(كريبتو|بيتكوين|crypto)|"
    r"double\s*your\s*(crypto|btc|eth)|ضاعف\s*.*(بيتكوين|عملت)|"
    r"claim\s*your\s*(gift|reward)|اضغط\s*هنا\s*.*(هدية|جائزة))",
    re.IGNORECASE,
)


@dataclass
class ScamCheckResult:
    is_scam: bool
    reasons: list[str]
    matched_domains: list[str]


def extract_urls(text: str) -> list[str]:
    return _URL_RE.findall(text or "")


def _extract_domain(url: str) -> str:
    if not url.lower().startswith(("http://", "https://")):
        url = "http://" + url
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


class ScamLinkDetector:
    def __init__(
        self,
        blacklist: set[str] | None = None,
        whitelist: set[str] | None = None,
    ):
        self.blacklist = set(blacklist) if blacklist else set(DOMAIN_BLACKLIST)
        self.whitelist = set(TRUSTED_DOMAINS)
        if whitelist:
            self.whitelist |= set(whitelist)

    def set_guild_whitelist(self, domains: list[str]) -> None:
        self.whitelist = set(TRUSTED_DOMAINS) | {d.lower() for d in domains}

    def check(self, text: str) -> ScamCheckResult:
        if not text:
            return ScamCheckResult(False, [], [])

        urls = extract_urls(text)
        reasons: list[str] = []
        matched_domains: list[str] = []

        for url in urls:
            domain = _extract_domain(url)
            if not domain or domain in self.whitelist:
                continue

            if domain in self.blacklist:
                reasons.append(f"domain_blacklist:{domain}")
                matched_domains.append(domain)
                continue

            if any(domain.endswith(tld) for tld in _SUSPICIOUS_TLDS) and _SUSPICIOUS_KEYWORD_RE.search(domain):
                reasons.append(f"suspicious_domain_pattern:{domain}")
                matched_domains.append(domain)
                continue

            if _SUSPICIOUS_KEYWORD_RE.search(domain):
                # Keyword-squatting on a normal TLD (e.g. discord-nitro.com)
                # is still worth flagging, just with a softer reason tag.
                reasons.append(f"suspicious_keyword_domain:{domain}")
                matched_domains.append(domain)

        if urls and _SCAM_PHRASE_RE.search(text):
            reasons.append("scam_phrase_with_link")

        return ScamCheckResult(is_scam=bool(reasons), reasons=reasons, matched_domains=matched_domains)
