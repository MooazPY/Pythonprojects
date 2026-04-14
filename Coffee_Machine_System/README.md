# ☕ Coffee Machine

A Python terminal simulation of a coffee vending machine. Order drinks, insert coins, check resources, and manage the machine — all from the command line!

---

## ✨ Features

- Order espresso, latte, or cappuccino
- Coin-based payment system (quarters, dimes, nickels, pennies)
- Change calculation and refund on insufficient payment
- Resource tracking for water, milk, and coffee
- `report` command to check current resource levels
- `off` command to shut down the machine
- Ingredient availability check before each order

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x

### Run the script

```bash
python Coffee_Machine.py
```

---

## 🖥️ Usage

```
What would you like? (espresso/latte/cappuccino): latte
Please insert coins.
How many quarters?: 4
How many dimes?: 2
How many nickles?: 0
How many pennies?: 0
Here is $0.20 in change.
Here is your latte ☕ Enjoy!
```

### Special Commands

| Command | Action |
|---------|--------|
| `report` | Displays current water, milk, coffee, and money levels |
| `off` | Shuts down the machine |

---

## ☕ Menu & Pricing

| Drink | Cost | Water | Milk | Coffee |
|-------|------|-------|------|--------|
| Espresso | $1.50 | 50ml | — | 18g |
| Latte | $2.50 | 200ml | 150ml | 24g |
| Cappuccino | $3.00 | 250ml | 100ml | 24g |

---

## ⚙️ How It Works

1. User selects a drink
2. Machine checks if ingredients are sufficient
3. User inserts coins — the machine calculates the total
4. If payment is enough, the drink is served and change is returned
5. Resources are deducted after each successful order
6. Revenue accumulates and is shown in the `report`

---

## 📁 Project Structure

```
Coffee_Machine/
├── Coffee_Machine.py    # Main machine logic
└── menu.py              # MENU dictionary with drinks, ingredients & costs
```

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
