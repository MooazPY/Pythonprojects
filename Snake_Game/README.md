# 🐍 Snake Game

A classic Snake game built using Python’s `turtle` module. Control the snake, eat food to grow longer, and avoid collisions to achieve the highest score!

---

## ✨ Features

- Smooth snake movement with keyboard controls
- Food spawning system
- Snake grows after eating food
- Collision detection:
  - Walls
  - Self (snake body)
- Real-time score tracking
- Game over screen

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
Controls:
  ↑ → Move Up
  ↓ → Move Down
  ← → Move Left
  → → Move Right

Goal:
- Eat food to grow the snake
- Avoid hitting the walls or yourself
- Try to achieve the highest score possible
```

---

## 📁 Project Structure

```
Snake-Game/
├── main.py         # Main game loop
├── snake.py        # Snake behavior and movement
├── food.py         # Food spawning logic
├── score.py        # Score handling and display
```

---

## ⚙️ How It Works

1. The game initializes the screen using the `turtle` module  
2. A snake object is created with multiple segments  
3. Food appears randomly on the screen  
4. Snake moves continuously in the chosen direction  
5. When the snake eats food:
   - It grows longer  
   - Score increases  
6. Game ends if:
   - Snake hits the wall  
   - Snake collides with itself  
7. Final score is displayed on game over  

---

## 👤 Author

**MooazPY** — https://github.com/MooazPY
