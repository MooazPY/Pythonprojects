# Haris Pro (حارس Pro) — Enterprise Arabic Moderation & AI Anti-Scam Discord Bot

**Haris Pro** (حارس Pro) is a commercial-grade, self-hosted Discord moderation bot built specifically for Arabic-speaking communities. Powered by **Hugging Face AI NLP models**, multi-layered Arabic obfuscation neutralization, zero-latency local SQLite database, and advanced anti-scam & anti-raid protection.

---

## 🌟 Key Commercial Features

| Feature | Description |
|---------|-------------|
| 🤖 **Hugging Face AI Integration** | Real-time Arabic toxicity, hate speech, and profanity detection using hosted NLP models (`aubmindlab/bert-base-arabertv02` / `MARBERT`) |
| ⚡ **Zero-Lag Offline Fallback** | Async API client (`aiohttp`) with sub-100ms execution. Seamlessly falls back to local dictionary filters if AI API is offline |
| 🔤 **Evasion-Proof Arabic Normalization** | Neutralizes zero-width spaces (`\u200b`), Tashkeel diacritics, Tatweel (`ـ`), Alef/Taa variants, repeated character spam (`كللللب`), and Arabizi numbers (`3`, `5`, `7`, `9`) |
| 🗄️ **Zero-Cost SQLite Storage** | 100% free local SQLite database (`bot_data.db`) with WAL mode — zero external cloud costs (no Firestore required) |
| 🔍 **`/analyze_text` Diagnostic Tool** | Live inspector allowing admins to test Arabic sentences and preview normalized text, dictionary matches, and Hugging Face AI confidence scores |
| 📊 **`/stats` Server Security Dashboard** | Real-time metrics tracking total deleted messages, issued warnings, applied mutes, and active AI protection status |
| 🛡️ **Scam Link & Phishing Filter** | 40+ known scam/typosquat domains + heuristic detection for fake Nitro and crypto scams with per-guild domain whitelisting |
| 🚨 **Anti-Raid Auto-Lockdown** | Mass-join detection with automatic channel lockdown and instant recovery using `/unlock` |
| ⚙️ **Auto-Mod Levels (`low` / `medium` / `high`)** | Pre-tuned presets for warn thresholds, mute durations, spam sensitivity, and raid limits |

---

## 📁 Project Architecture

```
arabic_mod_bot/
├── main.py                    # Main bot entry point & slash command sync
├── moderation.py              # Moderation actions, warn/mute logic, & logging
├── config/
│   ├── db_config.py           # SQLite database store & GuildConfig schema
│   └── auto_mod.py            # Low / Medium / High security presets
├── data/
│   ├── arabic_bad_words.json  # Editable Arabic bad words dictionary
│   └── scam_domains.json      # Known phishing & scam domain list
├── filters/
│   ├── hf_ai_classifier.py    # Hugging Face AI async classifier & fallback engine
│   ├── arabic_words.py        # Evasion-proof Arabic normalizer & regex filter
│   ├── scam_links.py          # Scam link & phishing URL detector
│   ├── spam_detection.py      # Spam & rate-limit tracker
│   └── raid_protection.py     # Mass join anti-raid tracker
├── cogs/
│   ├── moderation.py          # Message listener, AI filter pipeline, /analyze_text & /stats
│   └── setup.py               # Setup panel, /setup_ai, and whitelist/blacklist controls
├── utils/data_loader.py       # JSON dataset loader
├── tests/                     # Comprehensive Pytest suite
│   ├── test_arabic_words.py
│   ├── test_auto_mod.py
│   ├── test_db_config.py
│   ├── test_hf_ai_classifier.py
│   ├── test_moderation_helpers.py
│   ├── test_scam_links.py
│   └── test_spam_detection.py
├── Dockerfile                 # Container setup
├── docker-compose.yml         # One-command production deployment
├── requirements.txt           # Python dependencies
└── LICENSE (MIT)              # Full commercial license
```

---

## 🚀 Quick Start Guide

### 1. Discord Bot Token
Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications), enable **Message Content** and **Server Members** intents, and grant standard Administrator / Moderation permissions.

### 2. Environment Setup
Copy `.env.example` to `.env` and fill in your details:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
HUGGINGFACE_TOKEN=your_optional_hf_api_token_here
```

### 3. Local Installation & Launch
```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS
pip install -r requirements.txt
python main.py
```

### 4. Docker Deployment (Recommended)
```bash
docker compose up -d --build
```

---

## 🎮 Slash Commands Directory

| Command | Category | Description |
|---------|----------|-------------|
| `/setup` | Admin | Initial setup wizard: log channel, mute role, and security level |
| `/setup_ai` | Admin | Toggle AI toxicity filter and set confidence threshold (`0.50` to `0.95`) |
| `/analyze_text` | Moderator | Test Arabic text live to inspect normalizer, regex dictionary, and AI score |
| `/stats` | Moderator | Display server protection statistics (deleted messages, warnings, mutes) |
| `/config show` | Admin | Display full server security configuration |
| `/config set-level` | Admin | Change protection level (`low`, `medium`, `high`) |
| `/filter add-word` | Admin | Add custom word to server blacklist |
| `/filter remove-word` | Admin | Remove custom word from server blacklist |
| `/filter whitelist-domain` | Admin | Allow trusted domain exceptions for scam link filter |
| `/warn` | Moderator | Issue manual warning to a user |
| `/warnings check` | Moderator | Check user warning count and history |
| `/warnings clear` | Moderator | Reset warning count for a user |
| `/unlock` | Admin | Lift auto-lockdown following a raid |

---

## 🧪 Running Unit Tests

Run the complete test suite to verify 100% code correctness:
```bash
pytest
```

---

## 💼 Selling & Monetization Guide

Haris Pro is licensed under **MIT**, granting full rights to sell, rebrand, or host as a paid service:

1. **SaaS Hosting Model**: Host one instance of Haris Pro on a VPS ($5/mo) and offer it as a premium bot subscription for Discord communities.
2. **Turn-key Source Code Sales**: Sell the complete repository + Docker setup guide to server owners seeking a private, self-hosted Arabic moderation bot.
