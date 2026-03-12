import google.generativeai as genai
from app.config import settings
from app.prompt import SYSTEM_PROMPT

# Configure Gemini once at module level
genai.configure(api_key=settings.GEMINI_API_KEY)

_model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=SYSTEM_PROMPT,
)


async def get_gemini_response(
    user_message: str, chat_history: list[dict]
) -> str:
    """
    Send the user message along with prior chat history to Gemini
    and return the model's text response.

    chat_history is a list of dicts with keys "role" and "parts",
    where role is either "user" or "model".
    """
    chat = _model.start_chat(history=chat_history)
    response = await chat.send_message_async(user_message)
    return response.text
