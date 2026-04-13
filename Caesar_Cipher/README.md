# 🔐 Caesar Cipher

A simple command-line Caesar Cipher tool built in Python that lets you **encrypt** and **decrypt** messages using a shift-based algorithm.

---

## 📌 How It Works

The Caesar Cipher works by shifting each letter in a message by a fixed number of positions in the alphabet.

- **Encode:** shifts letters forward by the given number
- **Decode:** shifts letters backward to recover the original message
- Non-alphabet characters (spaces, numbers, symbols) are kept as-is

> Example: `"hello"` with shift `3` → `"khoor"`

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x

### Run the program

```bash
python main.py
```

---

## 🖥️ Usage

1. Choose a direction — `encode` or `decode`
2. Enter your message
3. Enter a shift number
4. Get your result instantly
5. Choose to run again or exit

```
Type 'encode' to encrypt, type 'decode' to decrypt:
> encode
Type your message:
> hello world
Type the shift number:
> 3
Here's the encoded result: khoor zruog.

Want to restart the cipher program?
Type 'yes' if you want to go again. Otherwise type 'no'.
```

---

## 📁 Project Structure

```
Caesar_Cipher/
├── main.py       # Main program logic
└── art.py        # ASCII art logo
```

---

## ⚠️ Limitations

- Only supports lowercase English letters
- Large shift numbers are handled via modulo (wraps around the alphabet)

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
