# 🤖 Discord Quran Bot

A lightweight Discord bot built with Python that sends a **random Quran page** to any channel on command — perfect for a daily wird (ورد يومي).

---

## ✨ Features

- Responds to the `$quran` command in any channel
- Sends a random Quran page image (pages 1–604)
- Images fetched from [searchtruth.com](https://www.searchtruth.com)
- Greets with **"الورد اليومي"** before sending the page

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- A Discord bot token — get one from the [Discord Developer Portal](https://discord.com/developers/applications)

### Install dependencies

```bash
pip install discord.py
```

### Setup

1. Clone the repo
2. Open `main.py` and replace the token placeholder:

```python
dis_token = "----------YOUR DISCORD TOKEN----------"
```

3. Run the bot:

```bash
python main.py
```

---

## 🖥️ Usage

In any Discord channel the bot has access to, type:

```
$quran
```

The bot will respond with:
```
الورد اليومي
https://www.searchtruth.com/quran/images/images1/042.jpg
```

---

## 📁 Project Structure

```
Discord_Quran_Bot/
└── main.py       # Bot logic
```

---

## ⚠️ Important

- **Never share your Discord token publicly.** Consider storing it in a `.env` file and loading it with `python-dotenv` for safety.
- Make sure the bot has **Send Messages** permission in your server.

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
