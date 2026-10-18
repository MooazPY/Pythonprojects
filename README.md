<div align="center">

# 🐍 Python Engineering & Systems Portfolio
### *Production Backends, Cloud Services, REST APIs, Automation & Algorithms*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white)](https://aws.amazon.com/ec2/)

<br/>

> A curated collection of 15+ software engineering projects demonstrating clean object-oriented design, RESTful backend architecture, cloud deployments, real-time automation, and interactive graphical systems.

</div>

---

## 📑 Table of Contents

- [🚀 Flagship Production Systems](#-flagship-production-systems)
- [📂 Portfolio Directory & Projects](#-portfolio-directory--projects)
  - [🌐 Automation & API Integrations](#-automation--api-integrations)
  - [🖥️ Desktop & GUI Applications](#️-desktop--gui-applications)
  - [🔐 Security & Systems](#-security--systems)
  - [🎮 Interactive Games & Simulations](#-interactive-games--simulations)
- [🛠️ Tech Stack & Dependencies](#️-tech-stack--dependencies)
- [🚀 Quickstart & Setup](#-quickstart--setup)
- [👨‍💻 Author & Connect](#-author--connect)

---

## 🚀 Flagship Production Systems

These are enterprise-grade containerized systems deployed to cloud infrastructure:

<table>
  <thead>
    <tr>
      <th>Project</th>
      <th>Description</th>
      <th>Key Technologies</th>
      <th>Repository / Source</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>🛡️ Haris Bot</b></td>
      <td>Arabic Discord moderation & anti-scam bot with Hugging Face AI text classification, SQLite WAL mode, anti-raid lockdown, and telemetry dashboard.</td>
      <td><code>Python</code> <code>Hugging Face</code> <code>SQLite WAL</code> <code>Docker</code> <code>AWS EC2</code></td>
      <td><a href="https://github.com/MooazPY/haris-bot"><b>View Repository ➔</b></a></td>
    </tr>
    <tr>
      <td><b>🩺 Liver Cancer Detection System</b></td>
      <td>End-to-end medical diagnosis pipeline (U-Net lesion segmentation + ResNet-50 classification) handling 70,000+ CT scans with sub-2s inference response time.</td>
      <td><code>FastAPI</code> <code>PyTorch</code> <code>Firebase Firestore</code> <code>Docker</code></td>
      <td><a href="https://github.com/MooazPY/LiverCancer-Project"><b>View Repository ➔</b></a></td>
    </tr>
    <tr>
      <td><b>📖 Discord Quran Bot Service</b></td>
      <td>Containerized cloud background daemon serving automated daily Quran image posts and verse lookups with 99% uptime.</td>
      <td><code>discord.py</code> <code>Docker Compose</code> <code>systemd</code> <code>GitHub Actions</code></td>
      <td><a href="https://github.com/MooazPY/quran-bot"><b>View Repository ➔</b></a></td>
    </tr>
  </tbody>
</table>

---

## 📂 Portfolio Directory & Projects

### 🌐 Automation & API Integrations

| Directory | Project | Description | Tech Stack |
| :--- | :--- | :--- | :--- |
| [`/Workout_Tracking`](./Workout_Tracking) | **NLP Workout Logger** | Parses natural language exercise descriptions (e.g. *"ran 5km in 30 mins"*) via Nutritionix API and automatically records calories and timestamps to Google Sheets via Sheety. | `Python`, `Requests`, `Nutritionix API`, `Sheety` |
| [`/ISS_Tracker`](./ISS_Tracker) | **ISS Overhead Tracker** | Polls live International Space Station telemetry and Sunrise/Sunset APIs; automatically dispatches an SMTP email notification when the ISS is overhead during dark hours. | `Python`, `REST APIs`, `SMTP`, `JSON` |
| [`/WebScraping`](./WebScraping) | **Empire Top 100 Scraper** | Automated web scraping pipeline parsing paginated DOM trees to extract, clean, and serialize cinema ranking data into structured storage. | `Python`, `BeautifulSoup4`, `Requests` |

---

### 🖥️ Desktop & GUI Applications

| Directory | Project | Description | Tech Stack |
| :--- | :--- | :--- | :--- |
| [`/Password_Manager`](./Password_Manager) | **Secure Password Vault** | Desktop credential generator and manager with master password authentication, clipboard integration, search indexing, and encrypted JSON storage. | `Python`, `Tkinter`, `JSON`, `Pyperclip` |
| [`/Quizzler`](./Quizzler) | **Interactive Quiz Engine** | Object-oriented desktop trivia application querying Open Trivia Database REST API with dynamic score tracking and timed answer verification. | `Python`, `Tkinter GUI`, `REST APIs`, `OOP` |

---

### 🔐 Security & Systems

| Directory | Project | Description | Tech Stack |
| :--- | :--- | :--- | :--- |
| [`/Caesar_Cipher`](./Caesar_Cipher) | **Cryptographic Shift Cipher** | Algorithmic implementation of substitution cipher supporting bidirectional encryption, custom modulo shift keys, and text sanitization. | `Python`, `Algorithms`, `Security` |
| [`/Coffee_Machine_System`](./Coffee_Machine_System) | **Vending Machine Simulator** | Strict OOP system modeling monetary transactions, inventory state machines, coin validation, and resource threshold management. | `Python`, `OOP`, `Design Patterns` |

---

### 🎮 Interactive Games & Simulations

| Directory | Project | Description | Tech Stack |
| :--- | :--- | :--- | :--- |
| [`/Snake_Game`](./Snake_Game) | **Classic Snake Arcade** | OOP implementation featuring dynamic segment linked-list rendering, collision detection algorithms, and persistent high-score logging. | `Python`, `Turtle Graphics`, `File I/O` |
| [`/Pong_game`](./Pong_game) | **Two-Player Retro Pong** | Two-player physics simulation modeling paddle deflection angles, ball velocity acceleration vectors, and scoreboard states. | `Python`, `Turtle Graphics` |
| [`/Turtle_Crossing`](./Turtle_Crossing) | **Frogger Arcade** | Lane-traffic simulation with incremental difficulty curves, randomized vehicular spawning, and obstacle collision boundaries. | `Python`, `Turtle Graphics` |
| [`/US_states`](./US_states) | **US Geography Quiz** | Educational coordinate-mapping game reading geographic CSV data to plot state names at exact map coordinates upon user input. | `Python`, `Pandas`, `Turtle Graphics` |
| [`/Hangman_Game`](./Hangman_Game) | **Hangman CLI** | Terminal-based word guessing game with dynamic ASCII visual stages and state validation. | `Python`, `ASCII Art` |
| [`/Higher-Lower Game`](./Higher-Lower%20Game) | **Higher-Lower Celebrity Game** | Follower count comparison engine with randomized dataset queries and streak scoring. | `Python`, `Data Structures` |
| [`/Turtles_Race`](./Turtles_Race) | **Multi-Turtle Racing Sim** | Stochastic simulation where multiple thread-like visual entities compete across a track with betting mechanics. | `Python`, `Turtle Graphics` |
| [`/Hirst_Painting`](./Hirst_Painting) | **Generative Dot Art** | Colorgram palette extraction from Damien Hirst paintings rendering procedural 10x10 generative artwork. | `Python`, `Colorgram`, `Turtle` |

---

## 🛠️ Tech Stack & Dependencies

```
Languages:        Python 3.10+, SQL, Bash
APIs & Web:       FastAPI, Flask, Requests, BeautifulSoup4, Sheety, Nutritionix
Databases:        SQLite, Firebase Firestore
Data & Math:      Pandas, NumPy
GUI & Visual:     Tkinter, Turtle Graphics, Colorgram
Cloud & DevOps:   Kubernetes, Docker, Docker Compose, AWS EC2, systemd, GitHub Actions
Testing:          Pytest, Unittest
```

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone Repository
```bash
git clone https://github.com/MooazPY/Pythonprojects.git
cd Pythonprojects
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Run Any Project
Navigate to the directory of choice and execute the primary entrypoint:

```bash
# Example: Run Secure Password Vault
cd Password_Manager
python main.py

# Example: Run Workout Tracking Automation
cd ../Workout_Tracking
python main.py
```

---

## 👨‍💻 Author & Connect

**Mooaz Rafaat**  
*DevOps Engineer & Backend Developer | IT Intern at e& (Etisalat Egypt)*

- 💼 **LinkedIn:** [linkedin.com/in/mooazraafat](https://www.linkedin.com/in/mooazraafat/)
- 🐙 **GitHub:** [@MooazPY](https://github.com/MooazPY)
- 📧 **Email:** [mooazrafaat11@gmail.com](mailto:mooazrafaat11@gmail.com)
- 📍 **Location:** Cairo, Egypt

