# 🗺️ US States Game

A Python Turtle geography quiz where you name all 50 US states from memory. Correct answers appear on the map in real time!

---

## ✨ Features

- Interactive US map as the game background
- Type a state name and it appears at the correct location on the map
- Score tracker showing progress out of 50
- Type `stop` anytime to quit and save missed states to a file
- Saves all states you missed to `missed_states.txt` for review

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- Turtle (built-in)
- pandas

```bash
pip install pandas
```

### Setup

1. Place the US map image and CSV file in the project folder
2. Update these two lines in `main.py` with your actual file paths:

```python
screen.bgpic(r'YOUR_PIC_FOR_BACKGROUND')
data = pd.read_csv(r'YOUR_CSV_FILE_PATH')
```

3. Run the game:

```bash
python main.py
```

---

## 🖥️ Gameplay

1. A dialog box prompts you to name a US state
2. Correct answers are written on the map at the state's location
3. The score updates in the dialog title (`X/50 States Correct`)
4. Type `stop` to end the session early
5. Any states you missed are saved to a `missed_states` file

---

## 📁 Project Structure

```
US_states/
├── main.py              # Game logic
├── blank_states_img.gif # US map background image
└── 50_states.csv        # State names with x/y coordinates
```

### CSV Format

The CSV file should have the following columns:

| state | x | y |
|-------|---|---|
| Alabama | 175 | -120 |
| Alaska | -275 | -220 |
| ... | ... | ... |

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
