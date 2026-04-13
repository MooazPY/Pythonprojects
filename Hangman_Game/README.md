# 🎮 Hangman Game

A classic terminal-based Hangman game built in Python. Guess the hidden word one letter at a time before you run out of lives!

---

## ✨ Features

- Random word selection from a built-in word list
- 6 lives to guess the word
- ASCII art hangman that updates with each wrong guess
- Tracks already-guessed letters to avoid duplicate penalties
- Win/lose detection with word reveal on loss

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x

### Run the game

```bash
python main.py
```

---

## 🖥️ Gameplay

```
 _    _
| |  | |
| |__| | __ _ _ __   __ _ _ __ ___   __ _ _ __
|  __  |/ _` | '_ \ / _` | '_ ` _ \ / _` | '_ \
| |  | | (_| | | | | (_| | | | | | | (_| | | | |
|_|  |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|

guess a letter: e
_ _ e _ _

guess a letter: z
You guessed z, that's not in the word, you lose a life.

  +---+
  |   |
  O   |
      |
      |
      |
=========
```

---

## 📁 Project Structure

```
Hangman_Game/
├── main.py       # Core game logic
├── arts.py       # ASCII art logo & hangman stages
└── words.py      # Word list
```

---

## ⚙️ How It Works

1. A random word is chosen and displayed as blanks (`_ _ _ _ _`)
2. The player guesses one letter at a time
3. Correct guesses reveal the letter in all its positions
4. Wrong guesses cost a life and update the hangman drawing
5. The game ends when the word is fully guessed or lives run out

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
