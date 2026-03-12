import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import get_db, close_db
from app.gemini_client import get_gemini_response
from app.parser import extract_booking_data, strip_booking_tag
from app.email_service import send_email_to_samantha
from app.models import ChatRequest, ChatResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SmileBot backend starting up")
    yield
    await close_db()
    logger.info("SmileBot backend shut down")


app = FastAPI(title="SmileBot API", version="1.0.0", lifespan=lifespan)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS — allow Botpress widget and any origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _mongo_history_to_gemini(history: list[dict]) -> list[dict]:
    """Convert stored chat docs into the format Gemini expects."""
    gemini_hist = []
    for msg in history:
        gemini_hist.append({"role": "user", "parts": [msg["user_message"]]})
        gemini_hist.append({"role": "model", "parts": [msg["bot_response"]]})
    return gemini_hist


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    db = await get_db()
    collection = db["chat_history"]

    # Fetch prior conversation for this session (last 20 turns)
    past_docs = (
        await collection.find({"session_id": req.session_id})
        .sort("timestamp", 1)
        .to_list(length=20)
    )

    gemini_history = _mongo_history_to_gemini(past_docs)

    # Get LLM response
    bot_raw = await get_gemini_response(req.message, gemini_history)

    # Check for booking data
    booking_data = extract_booking_data(bot_raw)
    booking_captured = False

    if booking_data:
        booking_captured = True
        # Store the lead
        await db["leads"].insert_one(
            {
                "session_id": req.session_id,
                **booking_data,
                "timestamp": datetime.now(timezone.utc),
            }
        )
        # Send email to Samantha
        send_email_to_samantha(booking_data)
        logger.info("Booking captured & email dispatched for %s", booking_data.get("name"))

    # Strip the JSON tag before sending reply to patient
    clean_reply = strip_booking_tag(bot_raw)

    # Persist this turn
    await collection.insert_one(
        {
            "session_id": req.session_id,
            "user_message": req.message,
            "bot_response": bot_raw,
            "timestamp": datetime.now(timezone.utc),
        }
    )

    return ChatResponse(reply=clean_reply, booking_captured=booking_captured)


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "SmileBot"}
