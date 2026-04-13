# 📈 Higher-Lower Game

A terminal-based Python game where you guess which famous person has more social media followers. Keep your streak going as long as you can!

---

## ✨ Features

- Compare two famous personalities head-to-head
- Score tracking — streak continues until you get one wrong
- No repeated matchups in the same round
- ASCII art logo and versus screen
- Data includes name, description, country, and follower count

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
    __  ___       __             
   / / / (_)___ _/ /_  ___  _____
  / /_/ / / __ `/ __ \/ _ \/ ___/
 / __  / / /_/ / / / /  __/ /    
/_/ /_/_/\__, /_/ /_/\___/_/     

Compare A: Cristiano Ronaldo, Footballer, from Portugal
 _    __
| |  / /____
| | / / ___/
| |/ (__  ) 
|___/____/  

Against B: Selena Gomez, Musician and Actress, from United States

Who has more followers? Type 'A' or 'B': A
You're right! Current score: 1
```

---

## 📁 Project Structure

```
Higher-Lower_Game/
├── main.py           # Core game logic
├── game_data.py      # Famous persons data
└── Game_Arts.py      # ASCII art logo & VS graphic
```

---

## ⚙️ How It Works

1. Two famous personalities are randomly selected
2. Their name, description, and country are displayed
3. You guess who has more followers — `A` or `B`
4. A correct guess adds to your score and the game continues
5. A wrong guess ends the game and reveals your final score
6. The winner of each round becomes the next round's `A` comparison

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
