<div align="center">

# ⚙️ DevOps Automation & Backend Engineering Suite
### *Cloud Services, REST APIs, Automation Pipelines, Security & Systems*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white)](https://aws.amazon.com/ec2/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://www.kernel.org/)

<br/>

> A modular software engineering suite showcasing production-grade backend APIs, cloud deployment configurations, automated asynchronous pipelines, DevSecOps encryption utilities, and system simulations.

</div>

---

## 📑 Table of Contents

- [🚀 Production Cloud & Backend Microservices](#-production-cloud--backend-microservices)
- [🔄 DevOps Automation, Telemetry & API Pipelines](#-devops-automation-telemetry--api-pipelines)
- [🛡️ DevSecOps, Cryptography & System Vaults](#️-devsecops-cryptography--system-vaults)
- [🧮 Interactive Systems & Algorithmic Simulations](#-interactive-systems--algorithmic-simulations)
- [🛠️ Infrastructure & Tech Stack](#️-infrastructure--tech-stack)
- [🚀 Quickstart & Environment Setup](#-quickstart--environment-setup)
- [👨‍💻 Author & Connect](#-author--connect)

---

## 🚀 Production Cloud & Backend Microservices

Production-ready backend services packaged for containerized deployment:

<table>
  <thead>
    <tr>
      <th>System</th>
      <th>DevOps & Architecture Highlights</th>
      <th>Infrastructure & Stack</th>
      <th>Source / Access</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>🛡️ Haris Security Microservice</b></td>
      <td>Enterprise Arabic moderation daemon running on AWS EC2 (Rocky Linux). Features Hugging Face AI inference, SQLite WAL mode, anti-raid channel lockdown, and real-time telemetry dashboard.</td>
      <td><code>AWS EC2</code> <code>Docker</code> <code>systemd</code> <code>SQLite WAL</code> <code>Python</code></td>
      <td><a href="https://github.com/MooazPY/haris-bot"><b>View Repository ➔</b></a></td>
    </tr>
    <tr>
      <td><b>🩺 AI Healthcare Diagnosis Backend</b></td>
      <td>3-stage deep learning inference backend (U-Net lesion segmentation + ResNet-50 classification) processing 70,000+ CT scans with sub-2s response latency. 15+ authenticated endpoints backed by Firestore NoSQL.</td>
      <td><code>FastAPI</code> <code>PyTorch</code> <code>Docker</code> <code>Firebase Firestore</code></td>
      <td><a href="./LiverCancerDetectionSystem"><b>View Project ➔</b></a></td>
    </tr>
    <tr>
      <td><b>📖 Discord Cloud Daemon Service</b></td>
      <td>Continuous background daemon deployed on AWS EC2 delivering scheduled daily Quran image posts and query responses with 99% uptime.</td>
      <td><code>Docker Compose</code> <code>systemd</code> <code>GitHub Actions CI</code> <code>Python</code></td>
      <td><a href="./bots/quran_bot"><b>View Project ➔</b></a></td>
    </tr>
  </tbody>
</table>

---

## 🔄 DevOps Automation, Telemetry & API Pipelines

Event-driven automation scripts, external API connectors, and telemetry collectors:

| Directory | Pipeline | Description | DevOps / Tech |
| :--- | :--- | :--- | :--- |
| [`/Workout_Tracking`](./Workout_Tracking) | **NLP Telemetry Pipeline** | Parses natural language exercise metrics via Nutritionix NLP API and automates serialized logging into Google Sheets via Sheety REST endpoints. | `REST APIs`, `HTTP Telemetry`, `JSON`, `Python` |
| [`/ISS_Tracker`](./ISS_Tracker) | **Real-Time Satellite Event Poller** | Polls live orbital coordinates and solar zenith angles; automatically triggers an authenticated SMTP alert notification during dark-sky transit windows. | `Event Automation`, `SMTP Alerts`, `REST`, `Python` |
| [`/WebScraping`](./WebScraping) | **Data Extraction Pipeline** | Automated web scraping engine parsing multi-page DOM trees, performing data sanitization, and generating structured offline dataset dumps. | `BeautifulSoup4`, `HTML Parsing`, `ETL Pipeline` |

---

## 🛡️ DevSecOps, Cryptography & System Vaults

Security implementations focusing on data integrity, state machines, and cryptographic algorithms:

| Directory | System | Description | Architecture Focus |
| :--- | :--- | :--- | :--- |
| [`/Password_Manager`](./Password_Manager) | **Encrypted Credential Vault** | Desktop credential storage engine with master key authentication, clipboard memory clearing, dynamic search indexing, and serialized JSON storage. | `Data Protection`, `Tkinter GUI`, `JSON Serialization` |
| [`/Caesar_Cipher`](./Caesar_Cipher) | **Cryptographic Shift Cipher** | Algorithmic substitution cipher engine handling bidirectional ASCII encryption, arbitrary shift keys, and character stream sanitization. | `Cryptography`, `Algorithms`, `Text Sanitization` |
| [`/Coffee_Machine_System`](./Coffee_Machine_System) | **Transactional State Machine** | Strict OOP system modeling monetary transactions, coin validation algorithms, inventory thresholds, and resource state transitions. | `OOP Design Patterns`, `State Machines` |

---

## 🧮 Interactive Systems & Algorithmic Simulations

Visual engines, coordinate-mapping systems, and algorithms:

| Directory | Simulation | Description | Stack |
| :--- | :--- | :--- | :--- |
| [`/Quizzler`](./Quizzler) | **Interactive Quiz Engine** | Trivia application consuming Open Trivia Database REST API with timed state verification. | `Tkinter GUI`, `REST APIs`, `OOP` |
| [`/Snake_Game`](./Snake_Game) | **Snake Engine** | Segment linked-list rendering, coordinate collision detection, and persistent file I/O score logging. | `Turtle Graphics`, `File I/O`, `Algorithms` |
| [`/Pong_game`](./Pong_game) | **Physics Simulation** | Two-player game modeling paddle deflection vectors and velocity acceleration physics. | `Physics Simulation`, `Turtle Graphics` |
| [`/Turtle_Crossing`](./Turtle_Crossing) | **Obstacle Collision Game** | Multi-lane traffic simulation with randomized vehicular obstacle generation. | `Object Boundaries`, `Game Loops` |
| [`/US_states`](./US_states) | **Geographic Mapping Game** | Coordinate mapping engine parsing regional CSV datasets to plot labels upon user query. | `Pandas DataFrames`, `Coordinate Mapping` |
| [`/Hangman_Game`](./Hangman_Game) | **Terminal Word Guessing** | CLI game featuring ASCII state diagrams, input sanitization, and lexical evaluation. | `CLI Architecture`, `ASCII Rendering` |
| [`/Higher-Lower Game`](./Higher-Lower%20Game) | **Comparison Engine** | Randomized dataset query engine evaluating high-cardinality social metrics. | `Data Structures`, `Randomization` |
| [`/Turtles_Race`](./Turtles_Race) | **Stochastic Simulation** | Multi-entity execution simulation modeling randomized race distributions. | `Simulation`, `Random Walks` |
| [`/Hirst_Painting`](./Hirst_Painting) | **Generative Art Generator** | Algorithmic color extraction from Damien Hirst paintings rendering 10x10 geometric art. | `Generative Algorithms`, `Colorgram` |

---

## 🛠️ Infrastructure & Tech Stack

```
Cloud & Orchestration:  Kubernetes, Docker, Docker Compose, AWS EC2, Linux (Rocky Linux 9, RHEL), systemd
CI/CD & Monitoring:     GitHub Actions, Prometheus, Grafana, Nginx, Bash
Backend & APIs:         FastAPI, Flask, RESTful API Design, Pydantic, Requests
Databases:              SQLite (WAL Mode), Firebase Firestore
Security & Testing:     AES Encryption, SSH Hardening, Pytest, Unittest
```

---

## 🚀 Quickstart & Environment Setup

```bash
# Clone repository
git clone https://github.com/MooazPY/Pythonprojects.git
cd Pythonprojects

# Setup Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r Workout_Tracking/requirements.txt  # Or target project directory
```

---

## 👨‍💻 Author & Connect

**Mooaz Rafaat**  
*DevOps Engineer & Backend Developer | IT Intern at e& (Etisalat Egypt)*

- 💼 **LinkedIn:** [linkedin.com/in/mooazraafat](https://www.linkedin.com/in/mooazraafat/)
- 🐙 **GitHub Profile:** [@MooazPY](https://github.com/MooazPY)
- 📧 **Email:** [mooazrafaat11@gmail.com](mailto:mooazrafaat11@gmail.com)
- 📍 **Location:** Cairo, Egypt
