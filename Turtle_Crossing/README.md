# 🐢 Turtle Crossing Game

A fast-paced, arcade-style Python game using the turtle module. Help the turtle cross the busy road without getting hit by oncoming traffic!

✨ Features
Progressive Difficulty: Cars move faster every time you successfully cross.

Score Tracking: Keeps track of your current level.

Collision Detection: Precise hit-box logic to detect crashes with cars.

Smooth Animation: Uses screen tracer logic for a stutter-free experience.

🚀 Getting Started
Prerequisites
Python 3.x

The turtle module (built into the Python Standard Library)

Run the game
Bash
python main.py

🖥️ Gameplay
Move Up: Press the "Up" arrow key to move the turtle forward.

Avoid Traffic: Do not touch any of the randomly generated colorful cars.

Level Up: Reach the top edge of the screen to increase your level and the speed of the cars.

Game Over: If a car hits your turtle, the game ends immediately.

📁 Project Structure
Turtle_Crossing/

main.py — The core game loop and screen initialization.

player.py — Defines the turtle's movement and starting position.

car_manager.py — Handles car generation, movement, and speed increases.

scoreboard_calc.py — Manages the level display and "Game Over" message.

⚙️ How It Works
Initialization: The game sets up a 600x600 canvas and initializes the player, car manager, and scoreboard.

The Loop: * The screen updates every 0.1 seconds.

A new car has a chance to spawn in every cycle.

The script constantly checks for collisions (distance < 20 pixels).

Winning Logic: When the player reaches the finish line, the turtle resets to the start, and the CarManager increments the car speed attribute.

👤 Author
MooazPY — github.com/MooazPY
