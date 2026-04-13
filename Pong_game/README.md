🏓 Pong Game
A classic arcade-style Pong game built with Python's Turtle graphics library. Play against a friend on the same keyboard and see who scores first!

✨ Features
Two-player local multiplayer (same keyboard)

Smooth paddle movement with keyboard controls

Increasing ball speed after each hit for more challenge

Score tracking for both left and right players

Visual net divider on the playing field

Ball physics with realistic bouncing

🎮 Controls
Player	Move Up	Move Down
Left Player (W/S)	W	S
Right Player (↑/↓)	↑ (Up Arrow)	↓ (Down Arrow)
🚀 Getting Started
Prerequisites
Python 3.x

Turtle graphics library (comes built-in with Python)

Run the game
bash
python main.py
🖥️ Gameplay
text
┌─────────────────────────────────────────┐
│                    │                    │
│     Score: 0   │   │   Score: 0        │
│         ┌─────┐│   │┌─────┐             │
│         │     ││   ││     │             │
│         │  ●  ││   ││  ●  │             │
│         │     ││   ││     │             │
│         └─────┘│   │└─────┘             │
│                    │                    │
└─────────────────────────────────────────┘
How to play:

Left player uses W (up) and S (down) to move their paddle

Right player uses ↑ (Up Arrow) and ↓ (Down Arrow)

Keep the ball from passing your paddle

Each time the ball passes your opponent's paddle, you score a point

The ball speeds up slightly after each paddle hit

First to reach the target score wins (or play until you exit)

📁 Project Structure
text
Pong_Game/
├── main.py           # Core game loop and initialization
├── paddle.py         # Paddle class for player movement
├── ball.py           # Ball class with movement and collision physics
├── ScoreBoard.py     # Score tracking and net drawing
└── README.md         # Game documentation
⚙️ How It Works
Setup: Creates a black 800x600 game window with two paddles and a ball

Movement: Paddles respond to keyboard inputs with smooth vertical movement

Ball Physics:

Ball moves continuously in X and Y directions

Bounces off top and bottom walls

Bounces off paddles with increasing speed

Scoring:

Left player scores when ball passes right paddle (x > 380)

Right player scores when ball passes left paddle (x < -380)

Score updates automatically on the screen

Speed Progression: Ball speed increases after each paddle hit (timer *= 0.9), making the game progressively harder

🎯 Game Mechanics
Event	Effect
Ball hits top/bottom wall	Y-direction reverses
Ball hits paddle	X-direction reverses, ball speed increases
Ball passes left paddle	Right player scores, ball resets
Ball passes right paddle	Left player scores, ball resets
Ball reset	Returns to center, speed resets to normal
🔧 Customization Options
You can modify the following in main.py:

python
# Change ball speed multiplier (lower = faster speed increase)
timer *= 0.9  # Change to 0.95 for slower speed increase

# Change window size
screen.setup(800, 600)  # Modify width and height

# Change scoring boundaries
if ball.xcor() > 380:  # Adjust this value
🐛 Known Issues
Ball can sometimes get stuck on paddles at very high speeds

Game doesn't have an automatic win condition (plays indefinitely)

🔮 Future Improvements
Add single-player vs AI mode

Implement win condition (first to 5/10 points)

Add sound effects for paddle hits and scoring

Create a start menu with difficulty selection

Add power-ups (larger paddle, slower ball, etc.)

👤 Author
MooazPY — github.com/MooazPY

