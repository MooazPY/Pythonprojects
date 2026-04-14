# 🌐 Web Scraping — Top 100 Movies

A Python web scraping script that extracts Empire Online's **Top 100 Movies of All Time** from a Wayback Machine archive and saves them in order to a text file.

---

## ✨ Features

- Scrapes movie titles from a cached Empire Online article
- Reverses the list to display from #1 to #100
- Saves all titles to a clean `movies.txt` file

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- requests
- beautifulsoup4

```bash
pip install requests beautifulsoup4
```

### Run the script

```bash
python main.py
```

---

## 📄 Output

After running, a `movies.txt` file is created in the same directory:

```
1. The Godfather
2. Raiders of the Lost Ark
3. Star Wars
...
100. The Dark Knight
```

---

## ⚙️ How It Works

1. Sends a GET request to the archived Empire Online page via Wayback Machine
2. Parses the HTML using BeautifulSoup
3. Finds all `<h3>` tags with class `title` to extract movie names
4. Reverses the list (site lists from 100 → 1)
5. Writes the ordered titles to `movies.txt`

---

## 📁 Project Structure

```
WebScraping/
├── main.py       # Scraping logic
└── movies.txt    # Output file (generated on run)
```

---

## 👤 Author

**MooazPY** — [github.com/MooazPY](https://github.com/MooazPY)
