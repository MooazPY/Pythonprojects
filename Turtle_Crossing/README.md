# 🐢 Turtle Crossing

A Frogger-inspired arcade game built with Python's Turtle graphics. Cross the road without getting hit by cars — and survive as long as you can as the traffic speeds up!

---

## ✨ Features

- Player-controlled turtle that moves up across the screen
- Randomly generated cars moving across the road
- Speed increases every time you successfully cross
- Score tracking with level progression
- Game over screen on collision

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x (Turtle is built-in, no extra installs needed)

### Run the game

```bash
python main.py
```

---

## 🕹️ Controls

| Key | Action |
|-----|--------|
| ⬆️ Up Arrow | Move turtle forward |

---

## ⚙️ How It Works

1. The turtle starts at the bottom of the screen
2. Press **Up** to move toward the other side
3. Avoid the cars — a collision ends the game
4. Reach the top to advance to the next level
5. Cars get faster with each level cleared

---

## 📁 Project Structure

```
Turtle_Crossing/
├── main.py            # Game loop & collision detection
├── player.py          # Player movement & reset logic
├── car_manager.py     # Car creation, movement & speed control
└── scoreboard_calc.py # Score display & game over screen
```

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
