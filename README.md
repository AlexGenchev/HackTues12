# Smart Box — Civic Complaint System

Smart Box is an open-source civic-tech project that lets citizens file municipal complaints by simply pressing a physical button on a Raspberry Pi, speaking their complaint aloud, and letting the system handle the rest. The recorded audio is automatically transcribed (Bulgarian speech-to-text via Groq Whisper), classified into the correct problem category, rewritten as a formal administrative letter by an AI language model, routed to the responsible municipal department, sent by email, and stored in a database — all without the citizen needing a smartphone, internet access, or any technical knowledge.

---

## System Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    Raspberry Pi (Field Device)            │
│                                                           │
│  [Button Press] ──→ arecord (WAV) ──→ POST /complaints/upload │
└────────────────────────────┬──────────────────────────────┘
                             │ multipart/form-data (WAV)
                             ▼
┌───────────────────────────────────────────────────────────┐
│                  Backend Server (FastAPI)                  │
│                                                           │
│  1. Save audio file                                       │
│  2. Groq Whisper ──→ transcribed_text (Bulgarian)         │
│  3. Groq LLM ──→ category / location / urgency            │
│  4. Municipality lookup (municipalities.py dict)          │
│  5. Groq LLM ──→ formal complaint letter (Bulgarian)      │
│  6. Email lookup (department_emails.py dict)              │
│  7. smtplib ──→ email to municipal department             │
│  8. SQLAlchemy ──→ SQLite (smart_box.db)                  │
└──────────────┬────────────────────────────┬───────────────┘
               │ REST API                   │ static files
               ▼                            ▼
┌──────────────────────┐      ┌─────────────────────────────┐
│  Admin Frontend      │      │  /audio/* (served by FastAPI)│
│  (frontend/*.html)   │      └─────────────────────────────┘
└──────────────────────┘
```

---

## Requirements

### Hardware
- Raspberry Pi (any model with GPIO — tested on Pi 4 and Pi Zero 2W)
- Momentary push button wired to GPIO pin **23** and GND
- USB microphone (ALSA device `plughw:2,0` — adjust in `raspberry/main.py` if needed)
- Network connection to the backend server

### Software
- Python 3.11+
- All Python dependencies listed in `requirements.txt`
- A [Groq API key](https://console.groq.com/) (free tier is sufficient)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) for sending emails

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/HackTues12.git
cd HackTues12
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS / Raspberry Pi:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the template and fill in real values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BACKEND_URL=http://<YOUR_SERVER_IP>:8000/complaints/upload
GROQ_API_KEY=gsk_...
EMAIL_SENDER=youraddress@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

> ⚠ **Never commit `.env` to version control.** It is already listed in `.gitignore`.

---

## How to Run

### Backend

```bash
# From the repo root with the virtualenv active:
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

### Frontend (Admin Panel)

Open `frontend/admin_panel.html` in a browser, or serve the `frontend/` folder with any static file server:

```bash
python -m http.server 3000 --directory frontend
```

### Raspberry Pi

Copy the repository (or at minimum the `raspberry/` folder and `.env`) to the Pi, then:

```bash
# Ensure gpiozero and requests are installed:
pip install gpiozero requests python-dotenv

# Run as root if GPIO access requires it:
python raspberry/main.py
```

The device is ready when you see:

```
Smart Box is ready. Press the button to record a complaint.
```

Press and hold the button to record, release to submit.

---

## Hardware Sanity Check

Before running the main script, verify that GPIO pin 23 is wired correctly:

```bash
python tests/test_button.py
```

Press the button — you should see `Button PRESSED` and `Button RELEASED` in the terminal.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/complaints/upload` | Upload WAV, run full AI pipeline |
| `GET`  | `/complaints?page=1&limit=20` | Paginated complaint list |
| `GET`  | `/complaints/{id}` | Single complaint detail (includes letter) |
| `GET`  | `/` | Health check |

---

## Project Structure

```
HackTues12/
├── .env.example              # Environment variable template
├── .gitignore
├── requirements.txt
├── README.md
│
├── raspberry/
│   └── main.py               # Pi script: button → record → upload
│
├── tests/
│   └── test_button.py        # GPIO hardware sanity check
│
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── models.py             # SQLAlchemy Complaint model
│   ├── database.py           # DB engine and session factory
│   ├── routes/
│   │   └── complaints.py     # /complaints endpoints + full pipeline
│   ├── services/
│   │   ├── transcription.py  # Groq Whisper STT
│   │   ├── classification.py # Groq LLM classify
│   │   ├── formalization.py  # Groq LLM formal letter
│   │   └── email_service.py  # smtplib email sending
│   └── data/
│       ├── municipalities.py      # Village→municipality lookup dict
│       └── department_emails.py   # Category+municipality→email dict
│
├── ai_agent/
│   ├── ai_agent.py           # Earlier Gemini-based prototype
│   └── automation.py         # Playwright form-filling prototype
│
└── frontend/
    ├── admin_panel.html
    ├── settings.html
    ├── statistics.html
    └── style.css
```

---

## License

MIT — see `LICENSE` for details.
