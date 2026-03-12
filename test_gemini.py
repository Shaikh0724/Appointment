import traceback
import google.generativeai as genai
from app.config import settings
from app.prompt import SYSTEM_PROMPT

genai.configure(api_key=settings.GEMINI_API_KEY)

try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    chat = model.start_chat(history=[])
    response = chat.send_message("Hey")
    print("SUCCESS:", response.text[:200])
except Exception:
    traceback.print_exc()
