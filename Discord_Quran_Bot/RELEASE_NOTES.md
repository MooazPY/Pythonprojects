# Release Notes

## v2.1.0 — Sale Ready

- Finalized sale-ready packaging and docs
- Confirmed _daily mode_ connects, sends, and exits cleanly
- Confirmed _serve mode_ connects and remains ready for slash commands
- Minimized privileged intent requirements by supporting slash commands without message content intent
- Updated README, changelog, and deployment instructions

## Installation

1. Copy `.env.example` to `.env` and fill in values.
2. Install dependencies:
   ```bash
   python -m venv .venv
   .venv/Scripts/Activate.ps1
   pip install -r requirements.txt
   ```
3. Add the bot token and default channel ID to `.env`.
4. Invite the bot with `applications.commands` and message/send permissions.

## How to Run

- Daily message mode:
  ```bash
  python main.py --daily
  ```
- Long-running serve mode:
  ```bash
  python main.py --serve
  ```
