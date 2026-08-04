# Discord Quran Bot

A polished, client-friendly Discord bot for sharing Quran ayahs and daily devotional content. It supports both scheduled daily delivery and a long-running server mode with slash commands.

## Features

- Slash commands: /quran, /translation, /surahinfo, /surah, /status, /setchannel, /settime, /setlanguage, /setbrand, /setcolor, /viewsettings, /help
- Rich embed output for Quran ayahs and translations with custom per-server color and branding
- Per-guild branding, language, and embed color configuration
- Daily delivery mode with auto-scheduling and translation support
- Usage analytics stored per guild for command popularity and performance monitoring
- Local settings storage with optional custom database path
- Free public Quran API integration via alquran.cloud
- No privileged message content intent required for normal slash command operation

## Installation

Install locally using the package metadata:

```bash
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -e .
```

Or install directly from source:

```bash
pip install .
```

## Setup

1. Copy the example environment file and fill in your values:
   ```bash
   copy .env.example .env
   ```
2. Create a Discord bot in the Developer Portal and copy the token.
3. Invite the bot to your server using an install link with `applications.commands` and these permissions:
   - Read Messages / View Channels
   - Send Messages
   - Use Slash Commands

## Running the bot

- Debug mode (prints a sample endpoint and exits):
  ```bash
  python main.py --print-url
  ```
- Daily mode (connects, sends one message, disconnects):
  ```bash
  python main.py --daily
  ```
- Serve mode (long-running bot):
  ```bash
  python main.py --serve
  ```

## Customization Guide

A non-technical buyer can change the following without editing code:

- Bot name and avatar from the Discord Developer Portal
- Default channel by using `/setchannel`
- Daily time and timezone by using `/settime`
- Default translation language by using `/setlanguage`
- Daily brand text by using `/setbrand`
- View current configuration with `/viewsettings`
- Daily branding text via the `DAILY_BRAND` environment variable
- Default translation language via `DEFAULT_LANGUAGE`
- Default embed color via `DEFAULT_EMBED_COLOR`
- Force instant command registration to a test server with `DISCORD_GUILD_ID`
- Store settings in a custom path with `GUILD_SETTINGS_PATH`

## For buyers

This bot is ready to deliver premium Quran content to Discord communities:

- Unique daily embeds that feel polished and modern
- Per-server branding and language customization
- Easy one-command setup for admins
- Installable with `pip install .` and deployable with Docker
- CI-ready with GitHub Actions to verify package health on every push

If the buyer wants legacy prefix-style commands, they can enable the Message Content Intent in the Developer Portal, but the bot is fully functional with slash commands alone.

## Docker

```bash
docker build -t quran-bot .
docker run --env-file .env quran-bot
```

## Changelog

- Replaced the old image-scraping flow with a public Quran API
- Split the bot into daily and serve modes
- Added slash commands and per-guild settings
- Added packaging and documentation for resale and self-hosting
