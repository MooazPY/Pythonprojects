# 🤖 Discord Bots Portfolio

A curated collection of commercial-grade, production-ready Discord bots built with **Python**, **discord.py**, **Hugging Face AI NLP**, **SQLite**, and **Docker**.

---

## 📂 Bots Overview

| Bot | Description | Tech Stack | Quick Link |
|---|---|---|---|
| 🛡️ **Haris Pro (حارس Pro)** | Enterprise Arabic Moderation & AI Anti-Scam Discord Bot with Hugging Face NLP, evasion neutralization, anti-raid, and SQLite storage | Python 3.11+, `discord.py`, Hugging Face AI, SQLite, Docker | [Explore Haris Pro](./arabic_mod_bot) |
| 📖 **Discord Quran Bot** | Interactive Discord bot for Quran page browsing, recitations, and Islamic verse lookup for communities | Python 3.11+, `discord.py`, Docker | [Explore Quran Bot](./quran_bot) |

---

## 🛡️ 1. Haris Pro (حارس Pro) — Arabic Moderation & AI Anti-Scam Bot

**Haris Pro** is a commercial-grade, self-hosted Discord moderation bot built specifically for Arabic-speaking communities. It neutralizes complex Arabic evasion tactics, leverages hosted Hugging Face AI models, and provides zero-cost local database storage.

### Key Features
- **🤖 Hugging Face AI Integration**: Real-time Arabic toxicity, hate speech, and profanity detection (`aubmindlab/bert-base-arabertv02` / `MARBERT`).
- **⚡ Zero-Lag Offline Fallback**: Non-blocking `aiohttp` API calls with automatic sub-100ms fallback to local dictionary filters if AI API is offline.
- **🔤 Evasion-Proof Arabic Normalization**: Strips zero-width invisible unicode characters (`\u200b`), diacritics (Tashkeel / Tatweel), letter variants, repeated letter spam (`كللللب`), and Arabizi number substitutions (`3`, `5`, `7`, `9`).
- **🛡️ Anti-Scam & Phishing Filter**: 40+ known scam domain blacklist + heuristic phrase matching for fake Nitro and crypto scams with per-guild domain whitelisting.
- **🚨 Anti-Raid Auto-Lockdown**: Mass-join detection triggering automatic channel lockdown, recoverable instantly via `/unlock`.
- **🔍 Diagnostic Tools**: `/analyze_text` live text inspector and `/stats` server security dashboard.
- **🗄️ Zero Cloud Cost**: Built on SQLite with WAL mode — 100% free local storage without external database fees.

📁 **Directory**: [`./arabic_mod_bot`](./arabic_mod_bot)  
📄 **Full Documentation**: [`./arabic_mod_bot/README.md`](./arabic_mod_bot/README.md)

---

## 📖 2. Discord Quran Bot

**Discord Quran Bot** is a feature-rich, high-performance bot designed for Islamic Discord communities, delivering Quranic pages, recitations, and verse search with high reliability and zero setup friction.

### Key Features
- **📖 Quran Page Browsing**: Retrieve high-quality Quran pages on command.
- **🎧 Audio Recitations**: Stream recitations from renowned Qaris directly in voice channels or text commands.
- **⚡ Fast & Containerized**: Docker & `docker-compose` ready for immediate production deployment.
- **🧪 Tested & Modular**: Built with clean architecture, typed configuration, and unit test coverage.

📁 **Directory**: [`./quran_bot`](./quran_bot)  
📄 **Full Documentation**: [`./quran_bot/README.md`](./quran_bot/README.md)

---

## 🚀 Quick Deployment Guide

Both bots include individual `Dockerfile` and `docker-compose.yml` configurations for effortless deployment on any Linux VPS or server.

```bash
# To run Haris Pro (Arabic Moderation Bot):
cd bots/arabic_mod_bot
docker compose up -d --build

# To run Discord Quran Bot:
cd bots/quran_bot
docker compose up -d --build
```
