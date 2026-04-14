# 🏋️ Workout Tracker

A Python script that uses **Nutritionix AI** to understand natural language exercise input and automatically logs your workouts — including exercise name, duration, and calories burned — to a **Google Sheet** via Sheety.

---

## ✨ Features

- Natural language input: just type what you did (e.g. `"ran 5km and did 20 pushups"`)
- Nutritionix API calculates duration and calories automatically
- Logs each exercise as a row in a Google Sheet with date and time
- Supports multiple exercises in a single input

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- requests

```bash
pip install requests
```

### API Setup

You'll need accounts and keys from two services:

**1. Nutritionix**
- Sign up at [nutritionix.com](https://www.nutritionix.com/business/api)
- Get your `App ID` and `API Key`

**2. Sheety**
- Sign up at [sheety.co](https://sheety.co)
- Connect a Google Sheet with columns: `date`, `time`, `exercise`, `duration`, `calories`
- Get your Bearer token and endpoint URL

### Configuration

Open `main.py` and fill in your credentials:

```python
BEARER_AUTH = "__Your Authentication key from sheety__"
API_KEY     = "__Your Api key from Nutritionix__"
APP_ID      = "__App id from Nutritionix__"
GENDER      = "male"   # or "female"
AGE         = "21"
```

### Run the script

```bash
python main.py
```

---

## 🖥️ Usage

```
Tell me which exercises you did: ran 3 miles and did 30 pushups

→ Logs to Google Sheet:
Date       | Time     | Exercise | Duration | Calories
14/4/2026  | 10:30:00 | Running  | 28       | 290
14/4/2026  | 10:30:00 | Pushups  | 5        | 34
```

---

## 📁 Project Structure

```
Workout_Tracking/
└── main.py    # All logic in one file
```

---

## ⚠️ Important

Never share your API keys publicly. Consider storing them in a `.env` file:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("NUTRITIONIX_API_KEY")
```

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
