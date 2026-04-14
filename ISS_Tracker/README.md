# 🌍 ISS Tracker

A Python script that tracks the **International Space Station** in real time and sends you an **email alert** when it's passing overhead at night — so you can step outside and spot it!

---

## ✨ Features

- Checks ISS position every 60 seconds via live API
- Detects if the ISS is within ±5° of your location
- Checks if it's currently dark at your location (between sunset and sunrise)
- Sends an email alert when both conditions are met

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- requests

```bash
pip install requests
```

### Setup

Open `ISS.py` and fill in your details:

```python
MY_EMAIL    = "YOUR_EMAIL_HERE"
MY_PASSWORD = "YOUR_PASSWORD_HERE"
MY_LAT      = 30.044420   # Your latitude
MY_LNG      = 31.235712   # Your longitude
```

Also update the SMTP address for your email provider:

```python
connection = smtplib.SMTP("YOUR_SMTP_ADDRESS_HERE")
```

| Email Provider | SMTP Address |
|---|---|
| Gmail | `smtp.gmail.com` |
| Outlook | `smtp.office365.com` |
| Yahoo | `smtp.mail.yahoo.com` |

> **Gmail users:** Use an [App Password](https://myaccount.google.com/apppasswords) instead of your real password.

### Run the script

```bash
python ISS.py
```

The script runs continuously, checking every 60 seconds.

---

## ⚙️ How It Works

1. Every 60 seconds, fetches the ISS's current latitude & longitude from [open-notify.org](http://api.open-notify.org/iss-now.json)
2. Checks if the ISS is within ±5° of your coordinates
3. Fetches sunrise/sunset times for your location from [sunrise-sunset.org](https://api.sunrise-sunset.org)
4. If it's dark **and** the ISS is overhead → sends you an email: **"Look Up 👆"**

---

## 📁 Project Structure

```
ISS/
└── ISS.py    # All logic in one file
```

---

## ⚠️ Important

Never commit your email credentials to GitHub. Store them in a `.env` file:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os
load_dotenv()
MY_EMAIL    = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")
```

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
