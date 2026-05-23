# Spiritual AI 🕉✝☪

AI-powered spiritual guidance drawing from the **Bhagavad Gita**, **Holy Bible**, and **Holy Quran**.  
Built with Flask + Mistral AI.

---

## Features

| Feature | Description |
|---|---|
| **Ask Guidance** | Pose any personal or spiritual question and receive wisdom from three traditions |
| **Journal** | Private journal with AI-generated spiritual reflections per entry |
| **Horoscope** | Daily horoscope based on your birth date + zodiac |
| **Numerology** | Life Path Number calculation with spiritual insight |
| **Meditation** | Guided breathing, mala counter, and meditation timer |
| **Pomodoro** | Sacred focus timer with spiritual quotes |
| **Contact** | Email contact form |

---

## Quick Start

### Prerequisites
- Python 3.11+
- A [Mistral AI](https://console.mistral.ai) API key

### Setup

```bash
# 1. Clone the project
git clone <your-repo-url>
cd spiritual-ai

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and fill in your API_KEY (required) and other values

# 5. Run in development
python main.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_KEY` | ✅ Yes | Mistral AI API key |
| `SECRET_KEY` | Recommended | Flask session secret (random string) |
| `MAIL_USER` | Optional | Gmail address for contact form |
| `MAIL_PASS` | Optional | Gmail App Password |
| `PORT` | Optional | Server port (default: 5000) |
| `FLASK_DEBUG` | Optional | Set `true` for dev mode (default: false) |

---

## Production Deployment

### Render / Heroku (Recommended)

1. Push your code to a Git repository
2. Connect the repo to Render or Heroku
3. Set environment variables in the dashboard
4. Render auto-detects the `Procfile` and deploys

### Docker

```bash
# Build image
docker build -t spiritual-ai .

# Run container
docker run -p 5000:5000 \
  -e API_KEY=your_key \
  -e SECRET_KEY=your_secret \
  spiritual-ai
```

### Manual (VPS / Server)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn (production)
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 main:app
```

Use **nginx** as a reverse proxy in front of Gunicorn for SSL and static file serving.

---

## Project Structure

```
spiritual-ai/
├── main.py                 # Flask app (single entry point)
├── requirements.txt        # Python dependencies
├── Procfile                # Heroku/Render process file
├── Dockerfile              # Container config
├── .env.example            # Environment template
├── .gitignore
├── journal_entries.json    # Auto-created: journal data (flat-file storage)
├── static/
│   ├── script.js           # Global JS (particles, BGM, nav)
│   ├── style.css           # Supplemental CSS
│   ├── BGM.mp3             # Ambient background music
│   ├── favicon.ico
│   └── images/             # App images
└── templates/
    ├── base.html           # Layout shell (navbar, footer, particles)
    ├── spiritual.html      # Home / Ask Guidance
    ├── journal.html        # Spiritual Journal
    ├── horoscope.html      # Daily Horoscope
    ├── numerology.html     # Life Path Numerology
    ├── meditation.html     # Meditation tools
    ├── pomodoro.html       # Focus timer
    ├── contact.html        # Contact form
    ├── 404.html            # Not Found
    └── 500.html            # Server Error
```

---

## Notes

- **Journal data** is stored in `journal_entries.json` (flat file). For production at scale, migrate to SQLite or PostgreSQL.
- **Mail** is optional — the contact form gracefully degrades if `MAIL_USER`/`MAIL_PASS` are not set.
- **BGM auto-play** is gated behind first user interaction to comply with browser autoplay policies.
