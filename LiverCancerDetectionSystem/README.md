# 🫀 Liver Care — AI-Powered Liver Cancer Detection System

> Early liver cancer detection using AI-powered CT scan analysis

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=flat-square&logo=flask)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange?style=flat-square&logo=firebase)
![AI](https://img.shields.io/badge/AI-Deep%20Learning-green?style=flat-square)

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Pages & Routes](#pages--routes)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)

---

## 📖 About

Liver Care is an AI-powered web platform for early liver cancer detection. It allows patients to upload CT scan images and receive an instant AI-generated analysis report. The system classifies tumors as **Benign** or **Malignant**, identifies cancer stage, tumor size, and location — all within seconds.

---

## ✨ Features

- 🔬 **AI CT Scan Analysis** — Upload a CT scan and get instant results
- 📊 **Admin Dashboard** — Real-time analytics and statistics
- 👤 **Patient Profiles** — Manage personal information and scan history
- 📋 **Medical Reports** — Detailed PDF-ready reports for each scan
- 🤖 **AI Medical Chatbot** — Liver health assistant powered by HuggingFace
- 📧 **Email Verification** — Secure registration with OTP verification
- 🔐 **Password Reset** — Email-based password recovery
- 👨‍⚕️ **Doctor Assignment** — Automatic doctor assignment for each patient
- 🔒 **Secure Authentication** — Hashed passwords, session management, HTTPS support

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | Firebase Firestore |
| AI Models | TensorFlow / Keras (.h5) |
| AI Chatbot | HuggingFace (Kimi-K2-Instruct) |
| Email | SMTP (Gmail) |
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| Security | Flask-Talisman, Werkzeug |

---

## 📁 Project Structure

```
LiverCancerDetectionSystem/
├── Flask/
│   ├── app.py                  # Main Flask application
│   ├── model_predictor.py      # AI model loading & prediction
│   ├── chatbotTest.py          # Chatbot testing script
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variables template
│   ├── static/
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript files
│   │   ├── images/             # Static images
│   │   └── ico/                # Favicon & icons
│   └── templates/
│       ├── index.html          # Home page
│       ├── login.html          # Login page
│       ├── register.html       # Registration page
│       ├── profile.html        # User profile
│       ├── my-results.html     # Scan history
│       ├── result.html         # Scan result page
│       ├── admin-dashboard.html# Admin analytics
│       ├── news.html           # Medical news
│       ├── contact-us.html     # Contact & AI chatbot
│       ├── faq.html            # Help & FAQ
│       ├── forgot-password.html# Password reset
│       ├── verify-email.html   # Email verification
│       ├── base.html           # Base template
├── Test Images/
│   ├── Cancer_Image.jpg
│   └── NoCancer_Image.jpg
├── firestore.indexes.json
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Firebase project with Firestore enabled
- Gmail account with App Password enabled
- HuggingFace account with API token

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/MooazPY/Pythonprojects.git
cd Pythonprojects/LiverCancerDetectionSystem/Flask
```

**2. Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

**5. Add Firebase service account**
- Go to Firebase Console → Project Settings → Service Accounts
- Generate a new private key
- Save it as `serviceAccountKey.json` inside the `Flask/` folder

**6. Deploy Firestore indexes**
```bash
firebase deploy --only firestore:indexes
```

**7. Run the application**
```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000`

---

## 🔐 Environment Variables

Create a `.env` file in the `Flask/` directory based on `.env.example`:

```env
# Flask Configuration
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Security
FORCE_HTTPS=False
SESSION_COOKIE_SECURE=False
SECRET_KEY=your_secret_key_here

# API Keys
HF_TOKEN=your_huggingface_token_here

# Admin Credentials
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your_strong_password

# SMTP Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM=Liver Care <your_email@gmail.com>
```

> ⚠️ **Never commit your `.env` or `serviceAccountKey.json` to GitHub!**

---

## 🗺 Pages & Routes

| Route | Page | Access |
|-------|------|--------|
| `/` | Home | Public |
| `/login.html` | Login | Public |
| `/register.html` | Register | Public |
| `/forgot-password.html` | Password Reset | Public |
| `/verify-email.html` | Email Verification | Public |
| `/profile.html` | User Profile | Logged in |
| `/my-results.html` | Scan History | Logged in |
| `/result.html` | Scan Result | Logged in |
| `/news.html` | Medical News | Public |
| `/contact-us.html` | Contact + Chatbot | Public |
| `/faq.html` | Help & FAQ | Public |
| `/admin-dashboard.html` | Admin Analytics | Admin only |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Upload CT scan for analysis |
| GET | `/api/my-results` | Get user's scan history |
| POST | `/api/chat` | AI medical chatbot |
| GET | `/api/admin/analytics` | Admin dashboard data |
| GET | `/api/get-doctor-info` | Get assigned doctor |
| POST | `/api/send-reset-code` | Send password reset OTP |
| POST | `/api/verify-reset-code` | Verify reset OTP |
| POST | `/api/reset-password` | Set new password |
| POST | `/api/verify-registration` | Complete email verification |
| GET | `/check-session` | Check login session |

---

## 📸 Screenshots

| Page | Preview |
|------|---------|
| Home | ![Home](../Test%20Images/NoCancer_Image.jpg) |

> Full screenshots available in the project folder.

---

## 👨‍💻 Author

- GitHub: [@MooazPY](https://github.com/MooazPY)

---

## 📄 License

This project was developed as a Final Year Computer Science Project.

---

> ⚠️ **Disclaimer:** This system provides AI-assisted preliminary analysis only. It does **not** replace professional medical diagnosis. Always consult a qualified healthcare professional.

