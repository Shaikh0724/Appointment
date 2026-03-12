# SmileBot — AI Virtual Receptionist for A Beautiful Smile

Zero-cost AI-powered receptionist that answers clinic FAQs, triages emergencies, captures appointment leads, and emails them to the office manager.

This project now includes a built-in web chat UI with voice input and voice replies at the root URL (`/`).

## Tech Stack (all free tier)

| Component       | Technology                                |
|-----------------|-------------------------------------------|
| AI / LLM        | Google Gemini Flash (`gemini-flash-latest`) |
| Backend         | FastAPI (Python)                          |
| Database         | MongoDB Atlas M0 (free cluster)           |
| Frontend Widget | Botpress Webchat                          |
| Email           | Python `smtplib` + Gmail App Password     |
| Hosting         | Render.com (free tier)                    |

## Project Structure

```
Appointment/
├── app/
│   ├── __init__.py
│   ├── config.py          # env var loading
│   ├── database.py        # MongoDB (motor) connection
│   ├── email_service.py   # smtplib email sender
│   ├── gemini_client.py   # Gemini API integration
│   ├── main.py            # FastAPI app & /chat endpoint
│   ├── models.py          # Pydantic request/response models
│   ├── parser.py          # BOOKING_DATA regex extractor
│   ├── prompt.py          # System prompt (knowledge base)
│   └── static/            # Built-in web UI + voice frontend
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── .env.example
├── .gitignore
├── Procfile
├── render.yaml
├── runtime.txt
├── requirements.txt
├── BOTPRESS_SETUP.md
└── README.md
```

## Quick Start (Local Development)

### 1. Clone & install
```bash
cd Appointment
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Create `.env`
Copy `.env.example` to `.env` and fill in your values:
```
GEMINI_API_KEY=<your Google AI Studio key>
MONGODB_URI=<your MongoDB Atlas connection string>
SMTP_EMAIL=<your Gmail address>
SMTP_APP_PASSWORD=<your Gmail App Password>
CLINIC_EMAIL=samantha@absjacksonvillenc.com
```

### 3. Run
```bash
uvicorn app.main:app --reload
```
Server starts at `http://127.0.0.1:8000`. Test the health check at `/health`.

- Web UI: `http://127.0.0.1:8000/`
- API Docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

### 4. Test the `/chat` endpoint
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-001", "message": "Hi, what services do you offer?"}'
```

## Deploy to Render

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com), create a **New Web Service** → connect your GitHub repo.
3. Render will auto-detect `render.yaml`. Add the environment variables in the Render dashboard.
4. Deploy. Your API will be live at `https://smilebot-api.onrender.com`.

## How It Works

1. User sends a message via the Botpress widget.
2. Botpress forwards the message to the `/chat` endpoint on Render.
3. FastAPI loads the session's chat history from MongoDB and sends it + the new message to Gemini.
4. Gemini responds (with the system prompt governing its behavior).
5. The backend checks the response for a `<BOOKING_DATA>` JSON block.
6. If found → the lead is saved to MongoDB and an email is sent to Samantha via Gmail SMTP.
7. The `<BOOKING_DATA>` tag is stripped, and the clean reply is returned to Botpress.

## Gmail App Password Setup

1. Enable **2-Step Verification** on your Gmail account.
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords).
3. Generate a password for "Mail" → "Other (SmileBot)".
4. Use that 16-character password as `SMTP_APP_PASSWORD`.
