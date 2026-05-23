"""
Spiritual AI — Production Entry Point
Flask application providing AI-powered spiritual guidance.
Uses Mistral AI (open-mistral-nemo model).
"""

import os
import json
import uuid
import logging
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from mistralai import Mistral
from dotenv import load_dotenv

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
)
log = logging.getLogger("spiritual-ai")

# ── Environment ────────────────────────────────────────────────────────────────
load_dotenv()

def _require(key: str) -> str:
    """Fetch a required env var and abort with a clear message if missing."""
    val = os.getenv(key, "").strip()
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val

API_KEY    = _require("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "spiritual-ai-secret-change-in-production")
MAIL_USER  = os.getenv("MAIL_USER", "")
MAIL_PASS  = os.getenv("MAIL_PASS", "")

# ── Flask App ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ── Mail ───────────────────────────────────────────────────────────────────────
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=MAIL_USER,
    MAIL_PASSWORD=MAIL_PASS,
)
mail = Mail(app)

# ── Mistral Client ─────────────────────────────────────────────────────────────
mistral = Mistral(api_key=API_KEY)
MODEL   = "open-mistral-nemo"

# ── AI System Prompts ──────────────────────────────────────────────────────────
SPIRITUAL_PROMPT = (
    "You are a spiritual guide providing insights based on Hindu, Islamic, and Christian teachings. "
    "When presented with a user's question about personal feelings or life challenges, respond by "
    "addressing the concern through the lens of these religious philosophies.\n\n"
    "Include references to:\n"
    "- Hinduism: Slokas from Bhagavad Gita, Upanishads, Vedas\n"
    "- Islam: Ayahs from the Quran and Hadiths\n"
    "- Christianity: Verses from the Bible\n\n"
    "IMPORTANT RULES:\n"
    "- DON'T mention you are an AI.\n"
    "- DON'T answer modern-day tech questions.\n"
    "- Keep response concise but include RELEVANT VERSES.\n"
    "- Include real-life examples from Mahabharata, Islamic history, and Biblical narratives.\n"
    "- ANSWER IN THE LANGUAGE THE QUESTION IS ASKED IN.\n"
    "- Format response as HTML using <strong> for bold. Remove unnecessary <br> tags.\n"
    "- DECLINE if the context is not related to spirituality."
)

JOURNAL_PROMPT = (
    "You are a compassionate spiritual guide. A seeker has written a personal journal entry. "
    "Read their reflection and offer a short, heartfelt spiritual response drawing from the "
    "Bhagavad Gita, Holy Bible, and Holy Quran equally. Keep it to 3–4 sentences maximum — "
    "warm, personal, uplifting. Format as plain text (no HTML). End with one relevant verse "
    "reference. ANSWER IN THE SAME LANGUAGE AS THE JOURNAL ENTRY."
)

# ── Numerology Data ────────────────────────────────────────────────────────────
NUMEROLOGY = {
    1: ("The Leader",
        "You are a natural-born leader, independent and ambitious. Sacred texts honour the One — "
        "the singular divine source. Embrace your originality; you are meant to pioneer new paths."),
    2: ("The Diplomat",
        "You embody balance and cooperation. Like the two wings of a bird, you bring harmony. "
        "The Quran speaks of pairs in creation — you are the bridge between worlds."),
    3: ("The Creator",
        "Creative, expressive, joyful. The Trinity in Christianity; Brahma, Vishnu, Shiva in "
        "Hinduism — all speak to the sacred power of three."),
    4: ("The Builder",
        "Disciplined, stable, trustworthy. The four Vedas, four Gospels, four sacred angels — "
        "you are the foundation upon which great things are built."),
    5: ("The Adventurer",
        "Freedom-loving, curious, dynamic. The five pillars of Islam, the five Pandavas — you are "
        "guided by sacred freedom and divine adventure."),
    6: ("The Nurturer",
        "Loving, responsible, healing. The six days of creation, the six-pointed Star of David — "
        "you carry the vibration of divine love and service."),
    7: ("The Seeker",
        "Introspective, spiritual, wise. Seven heavens in Islam, seven chakras in Hinduism, seven "
        "days of creation — you are destined for deep spiritual truth."),
    8: ("The Achiever",
        "Powerful, authoritative, abundant. The figure-8 is infinity — you operate between the "
        "material and spiritual worlds with great karmic force."),
    9: ("The Humanitarian",
        "Compassionate, selfless, universal. Nine is the number of completion and divine love. "
        "The Gita's 9th chapter is called Raja-Vidya — the king of knowledge."),
}

# ── Bhagavad Gita Quotes (used on home page) ──────────────────────────────────
GITA_QUOTES = [
    "O son of Kunti, the nonpermanent appearance of happiness and distress… arise from sense "
    "perception, and one must learn to tolerate them without being disturbed. — Bhagavad Gita 2.14",
    "For the soul there is neither birth nor death at any time. He is unborn, eternal, "
    "ever-existing, and primeval. He is not slain when the body is slain. — Bhagavad Gita 2.20",
    "One who is not disturbed in mind even amidst the threefold misery or elated when there is "
    "happiness, and who is free from attachment, fear and anger, is called a sage of steady mind. "
    "— Bhagavad Gita 2.56",
    "As a lamp in a windless place does not waver, so the transcendentalist, whose mind is "
    "controlled, remains always steady in his meditation on the transcendent self. "
    "— Bhagavad Gita 6.19",
    "There is no truth superior to Me. Everything rests upon Me, as pearls are strung on a thread. "
    "— Bhagavad Gita 7.7",
    "Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all "
    "sinful reactions. Do not fear. — Bhagavad Gita 18.66",
]

import random
def random_quote() -> str:
    return random.choice(GITA_QUOTES)


# ── AI Helpers ─────────────────────────────────────────────────────────────────
def ask_spiritual(question: str) -> str:
    """Send a spiritual question to the AI and return HTML-formatted guidance."""
    try:
        prompt = f"{SPIRITUAL_PROMPT}\n\nQuestion: {question}\n\nNOW ANSWER THE ABOVE."
        resp = mistral.chat.complete(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
    except Exception as exc:
        log.error("Mistral API error (spiritual): %s", exc)
        return "<p>Could not reach the guidance server. Please try again shortly.</p>"


def ask_journal_reflection(entry_text: str) -> str:
    """Generate a short spiritual reflection for a journal entry."""
    try:
        prompt = f"{JOURNAL_PROMPT}\n\nJournal Entry:\n{entry_text}"
        resp = mistral.chat.complete(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
    except Exception as exc:
        log.error("Mistral API error (journal): %s", exc)
        return "Peace be with you on your journey. Every moment of reflection is sacred."


# ── Numerology Helper ──────────────────────────────────────────────────────────
def life_path_number(date_str: str) -> int:
    """Reduce a YYYY-MM-DD date string to a single-digit life-path number."""
    digits = [int(c) for c in date_str.replace("-", "") if c.isdigit()]
    total  = sum(digits)
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total


# ── Zodiac / Horoscope Helpers ─────────────────────────────────────────────────
def zodiac_sign(dt: datetime) -> str:
    d, m = dt.day, dt.month
    signs = {
        1:  ("Capricorn", "Aquarius",    20),
        2:  ("Aquarius",  "Pisces",      19),
        3:  ("Pisces",    "Aries",       21),
        4:  ("Aries",     "Taurus",      20),
        5:  ("Taurus",    "Gemini",      21),
        6:  ("Gemini",    "Cancer",      21),
        7:  ("Cancer",    "Leo",         23),
        8:  ("Leo",       "Virgo",       23),
        9:  ("Virgo",     "Libra",       23),
        10: ("Libra",     "Scorpio",     23),
        11: ("Scorpio",   "Sagittarius", 22),
        12: ("Sagittarius","Capricorn",  22),
    }
    first, second, cutoff = signs[m]
    return first if d < cutoff else second


def fetch_horoscope(sign: str) -> str:
    """Generate a daily horoscope using Mistral AI (no external API dependency)."""
    today = datetime.now().strftime("%B %d, %Y")
    prompt = (
        f"You are a wise Vedic and Western astrologer. Write a warm, insightful daily horoscope "
        f"for {sign} for {today}. Cover: energy of the day, love/relationships, career/focus, "
        f"and a spiritual tip. Keep it to 4-5 sentences, uplifting and specific to {sign}'s traits. "
        f"End with one relevant quote from the Bhagavad Gita, Bible, or Quran. Plain text only, no headers."
    )
    try:
        resp = mistral.chat.complete(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
    except Exception as exc:
        log.error("Mistral horoscope error: %s", exc)
        return "The cosmos are reflecting deeply today. Take time for stillness and inner guidance."


# ── Journal Storage (flat-file) ────────────────────────────────────────────────
JOURNAL_FILE = os.path.join(os.path.dirname(__file__), "journal_entries.json")
MAX_ENTRIES  = 100


def _load_journal() -> list:
    if os.path.exists(JOURNAL_FILE):
        try:
            with open(JOURNAL_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            log.error("Could not read journal file: %s", exc)
    return []


def _save_journal(entries: list) -> None:
    try:
        with open(JOURNAL_FILE, "w", encoding="utf-8") as fh:
            json.dump(entries, fh, indent=2, ensure_ascii=False)
    except OSError as exc:
        log.error("Could not write journal file: %s", exc)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())[:8]

    question = res = mood = None
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        mood     = request.form.get("mood", "")
        if question:
            res = ask_spiritual(question)

    return render_template(
        "spiritual.html",
        question=question,
        res=res,
        mood=mood,
        quote=random_quote(),
    )


@app.route("/rate", methods=["POST"])
def rate():
    """Lightweight rating endpoint — accepts star ratings, returns OK."""
    data = request.get_json(silent=True) or {}
    log.info("Rating received: %s stars for question: %s", data.get("rating"), data.get("question", "")[:60])
    return jsonify({"ok": True})


@app.route("/horoscope", methods=["GET", "POST"])
def horoscope():
    selected_date = zodiac = horo = ""
    if request.method == "POST":
        selected_date = request.form.get("date", "")
        try:
            dt     = datetime.strptime(selected_date, "%Y-%m-%d")
            zodiac = zodiac_sign(dt)
            horo   = fetch_horoscope(zodiac)
        except ValueError:
            horo = "Invalid date. Please select a valid birth date."

    return render_template(
        "horoscope.html",
        selected_date=selected_date,
        zodiac_sign=zodiac,
        horoscope=horo,
    )


@app.route("/numerology", methods=["GET", "POST"])
def numerology():
    selected_date = num = insight = tagline = ""
    if request.method == "POST":
        selected_date = request.form.get("date", "")
        try:
            datetime.strptime(selected_date, "%Y-%m-%d")   # validate
            num = life_path_number(selected_date)
            tagline, insight = NUMEROLOGY.get(num, ("Mystic", "Your number carries deep spiritual significance."))
        except ValueError:
            insight = "Invalid date. Please select a valid birth date."

    return render_template(
        "numerology.html",
        selected_date=selected_date,
        numerology_number=num,
        insight=insight,
        tagline=tagline,
    )


@app.route("/meditation")
def meditation():
    return render_template("meditation.html")


@app.route("/pomodoro")
def pomodoro():
    return render_template("pomodoro.html")


# ── Journal routes ─────────────────────────────────────────────────────────────

@app.route("/journal")
def journal():
    return render_template("journal.html", entries=_load_journal())


@app.route("/journal/save", methods=["POST"])
def journal_save():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Entry cannot be empty."}), 400

    reflection = ask_journal_reflection(text)
    now = datetime.now()
    entry = {
        "id":         str(uuid.uuid4())[:8],
        "text":       text,
        "mood":       data.get("mood", ""),
        "tags":       data.get("tags", []),
        "reflection": reflection,
        "date":       now.strftime("%B %d, %Y"),
        "time":       now.strftime("%I:%M %p"),
        "timestamp":  now.isoformat(),
    }

    entries = _load_journal()
    entries.insert(0, entry)
    if len(entries) > MAX_ENTRIES:
        entries = entries[:MAX_ENTRIES]
    _save_journal(entries)

    return jsonify({"ok": True, "entry": entry})


@app.route("/journal/delete", methods=["POST"])
def journal_delete():
    data     = request.get_json(silent=True) or {}
    entry_id = data.get("id")
    if not entry_id:
        return jsonify({"ok": False, "error": "No id provided."}), 400

    entries = [e for e in _load_journal() if e.get("id") != entry_id]
    _save_journal(entries)
    return jsonify({"ok": True})


# ── Contact route ──────────────────────────────────────────────────────────────

@app.route("/contact", methods=["GET", "POST"])
def contact():
    success = error = None
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email     = request.form.get("email", "").strip()
        phone     = request.form.get("phone", "").strip()
        subject   = request.form.get("subject", "").strip()
        message   = request.form.get("message", "").strip()

        if not all([full_name, email, subject, message]):
            error = "Please fill in all required fields."
        elif not MAIL_USER or not MAIL_PASS:
            error = "Mail service is not configured. Please reach out via email directly."
        else:
            try:
                msg = Message(
                    subject=f"Spiritual AI Contact: {subject}",
                    sender=MAIL_USER,
                    recipients=[MAIL_USER],
                    body=(
                        f"From: {full_name} <{email}>\n"
                        f"Phone: {phone}\n\n"
                        f"{message}"
                    ),
                )
                mail.send(msg)
                success = True
            except Exception as exc:
                log.error("Mail send failed: %s", exc)
                error = "Failed to send message. Please try again or email us directly."

    return render_template("contact.html", success=success, error=error)


# ── Error Handlers ─────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    log.error("500 error: %s", e)
    return render_template("500.html"), 500


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
