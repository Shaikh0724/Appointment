import re
import json
import logging

logger = logging.getLogger(__name__)


def extract_booking_data(bot_response: str) -> dict | None:
    """
    Parse the bot response for a <BOOKING_DATA>...</BOOKING_DATA> block.
    Returns the parsed dict if found, otherwise None.
    """
    pattern = r"<BOOKING_DATA>\s*(\{.*?\})\s*</BOOKING_DATA>"
    match = re.search(pattern, bot_response, re.DOTALL)

    if not match:
        return None

    try:
        data = json.loads(match.group(1))
        # Validate required fields
        required = ("name", "phone", "email", "preferred_time")
        if all(data.get(k) for k in required):
            return data
        logger.warning("Booking data missing required fields: %s", data)
        return None
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse booking JSON: %s", exc)
        return None


def strip_booking_tag(bot_response: str) -> str:
    """
    Remove the <BOOKING_DATA>...</BOOKING_DATA> block from the response
    so the patient never sees the raw JSON in the chat widget.
    """
    return re.sub(
        r"<BOOKING_DATA>\s*\{.*?\}\s*</BOOKING_DATA>",
        "",
        bot_response,
        flags=re.DOTALL,
    ).strip()
