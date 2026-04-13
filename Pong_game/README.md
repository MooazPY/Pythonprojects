# 🏓 Pong Game

A classic two-player Pong game built with Python’s `turtle` module. Control your paddle, bounce the ball, and compete to outscore your opponent!

---

## ✨ Features

- Two-player local gameplay
- Smooth paddle controls using keyboard
- Real-time ball movement and collision detection
- Ball speed increases after each hit
- Score tracking system
- Center net for classic Pong look

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
Player 1 (Left Paddle)
  W → Move Up
  S → Move Down

Player 2 (Right Paddle)
  ↑ → Move Up
  ↓ → Move Down

Goal:
- Hit the ball past your opponent’s paddle to score
- First to keep scoring wins (no limit unless you add one)
```

---

## 📁 Project Structure

```
Pong-Game/
├── main.py           # Main game loop and logic
├── paddle.py         # Paddle class (movement & controls)
├── ball.py           # Ball behavior and physics
├── ScoreBoard.py     # Score tracking and display
```

---

## ⚙️ How It Works

1. The game initializes the screen using the `turtle` module  
2. Two paddles are created on opposite sides of the screen  
3. The ball moves continuously across the screen  
4. Collisions are handled:
   - Top/Bottom → ball bounces vertically  
   - Paddles → ball bounces horizontally and speeds up  
5. If the ball passes a paddle:
   - Opponent scores a point  
   - Ball resets to center  
6. Game continues indefinitely until the window is closed  

---

## 👤 Author

**MooazPY** — https://github.com/MooazPY
