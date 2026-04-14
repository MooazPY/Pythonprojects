# 🔑 Password Manager

A desktop GUI application built with Python and Tkinter that lets you **generate**, **save**, and **search** passwords for your websites — all stored locally in a JSON file.

---

## ✨ Features

- Generate strong random passwords (letters + numbers + symbols)
- Save website credentials (website, email, password) to a local JSON file
- Search saved credentials by website name
- Simple and clean GUI with a logo
- Input validation — warns if any field is left empty

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x (Tkinter is built-in, no extra installs needed)

### Setup

1. Place your logo image in the project folder
2. Update the image path in `main.py`:

```python
pic = PhotoImage(file=r"YOUR_LOGO_PATH_HERE")
```

3. Run the app:

```bash
python Passowrd_Manager.py
```

---

## 🖥️ Usage

| Action | How |
|--------|-----|
| **Generate Password** | Click *Generate Password* to fill the password field automatically |
| **Save Credentials** | Fill in website, email, and password then click *Add* |
| **Search Website** | Type the website name and click *Search* |

Credentials are saved to a `pass.json` file in the project folder:

```json
{
    "github.com": {
        "email": "user@example.com",
        "password": "aB3$kL9!mN2#"
    }
}
```

---

## ⚙️ Password Generator

Each generated password contains:

- 8–10 random letters (upper & lowercase)
- 2–4 random numbers
- 2–4 random symbols (`!`, `#`, `$`, `%`, `&`, etc.)
- Shuffled randomly for extra security

---

## 📁 Project Structure

```
Password_Manager/
├── Passowrd_Manager.py    # Main app
├── logo.png               # App logo image
└── pass.json              # Generated credentials file (created on first save)
```

---

## ⚠️ Important

Passwords are stored in **plain text** inside `pass.json`. Do not share this file or upload it to GitHub. Add it to your `.gitignore`:

```
pass.json
```

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
