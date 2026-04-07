import logging
import time
import asyncio
import httpx
from app.config import settings
from app.prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

OPENAI_TIMEOUT = 10  # 10 second timeout


async def get_openai_response(
    user_message: str, chat_history: list[dict]
) -> str:
    """
    Send the user message along with prior chat history to OpenAI GPT-4
    and return the model's text response using direct API call.
    
    chat_history contains documents with 'user_message' and 'bot_response' keys.
    """
    start_time = time.time()
    
    # Convert chat history - use actual user and bot messages from database
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for msg in chat_history:
        # Check if this is database format (has user_message/bot_response) or OpenAI format (has parts)
        if "user_message" in msg:
            messages.append({"role": "user", "content": msg["user_message"]})
            messages.append({"role": "assistant", "content": msg["bot_response"]})
        elif "parts" in msg:
            # Fallback for OpenAI format
            messages.append({"role": "user" if msg.get("role") == "user" else "assistant", "content": msg["parts"][0]})
    
    messages.append({"role": "user", "content": user_message})
    
    logger.info(f"[OPENAI] Starting API call with {len(chat_history)} history items")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await asyncio.wait_for(
                client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                ),
                timeout=OPENAI_TIMEOUT
            )
        
        response_time = time.time()
        elapsed = response_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"[OPENAI] Response received in {elapsed:.2f}s")
            return data["choices"][0]["message"]["content"]
        else:
            logger.error(f"[OPENAI] API Error {response.status_code}: {response.text}")
            return "I'm having trouble processing your request. Please try again."
        
    except asyncio.TimeoutError:
        logger.warning(f"[OPENAI] Timeout after {OPENAI_TIMEOUT}s")
        return "I apologize, but I'm experiencing a temporary delay. Please try again in a moment."
    except Exception as e:
        logger.error(f"[OPENAI] Error: {str(e)}")
        return "I'm having trouble processing your request. Please try again."


# Backward compatibility - alias for existing code
get_gemini_response = get_openai_response
