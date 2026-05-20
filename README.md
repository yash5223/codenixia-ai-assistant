# Codenixia AI Business Assistant

AI-powered business automation system built with FastAPI and Groq (LLaMA 3.3 70B). Handles intelligent chat, lead capture, email automation, and admin reporting in a single deployable service.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| AI | Groq API — `llama-3.3-70b-versatile` |
| Database | SQLite |
| Frontend | Vanilla JS + Tailwind CSS |
| Email | Gmail SMTP |
| Deployment | Render |

---

## Architecture

```
Browser (index.html / dashboard.html)
           │
           │  REST API
           ▼
    FastAPI (main.py)
    ├── POST /api/chat   ──▶  Groq API (LLaMA 3.3 70B)
    ├── POST /api/leads  ──▶  SQLite + Gmail SMTP
    ├── GET  /api/leads  ──▶  SQLite
    └── GET  /api/stats  ──▶  SQLite
```

---

## Features

- **AI Chatbot** — LLaMA 3.3 70B via Groq with full conversation history
- **Lead Capture** — Contact form with name, email, phone, company, message
- **Data Storage** — SQLite with `leads` and `chats` tables
- **Email Automation** — Gmail notification triggered on every new lead
- **Admin Dashboard** — Live stats, lead table, CSV export (password: `admin123`)

---

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/codenixia-ai-assistant
cd codenixia-ai-assistant
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GROQ_API_KEY=gsk_your_groq_key_here
SMTP_USER=yourname@gmail.com
SMTP_PASS=your_gmail_app_password
```

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000`

> **Gmail App Password:** Google Account → Security → 2-Step Verification → App Passwords

> **Groq API Key:** [console.groq.com](https://console.groq.com) → API Keys

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | From [console.groq.com](https://console.groq.com) |
| `SMTP_USER` | Optional | Gmail address for lead notifications |
| `SMTP_PASS` | Optional | Gmail App Password |

---

## API Reference

**POST `/api/chat`**
```json
{ "message": "string", "history": [] }
→ { "reply": "string" }
```

**POST `/api/leads`**
```json
{ "name": "string", "email": "string", "phone": "string", "company": "string", "message": "string" }
→ { "status": "success", "msg": "string" }
```

**GET `/api/leads`** — Returns all leads ordered by date

**GET `/api/stats`** — Returns `{ leads, chats, today_leads }`

---

## Deployment (Render)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repo — Render auto-detects `render.yaml`
4. Add environment variables in the Render dashboard
5. Deploy

---

## Project Structure

```
├── main.py              # FastAPI backend
├── requirements.txt     # Dependencies
├── Procfile             # Process command
├── render.yaml          # Render deployment config
├── .env.example         # Environment variable template
├── .gitignore
├── README.md
└── static/
    ├── index.html       # Chat + lead form UI
    └── dashboard.html   # Admin dashboard
```

---

## Automation Workflow

```
User submits lead form
        ↓
Data validated and stored in SQLite
        ↓
Gmail SMTP sends notification email to admin
        ↓
User receives success confirmation
```
