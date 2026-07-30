"""
app/rag/lead_flow.py
--------------------
Multi-turn conversational lead capture state machine.

When intent == "lead", this module takes over from the normal RAG chain.
It asks: name → email → requirement across 3 turns, then writes to Supabase.

State is stored in a separate dict keyed by session_id.
States: "ask_name" → "ask_email" → "ask_requirement" → "complete"
"""

import logging
import re
from typing import Tuple

from app.utils.database import save_lead

logger = logging.getLogger(__name__)

# Lead state per session
_lead_states: dict = {}

# Messages the bot sends at each step
MESSAGES = {
    "start": (
        "Great! I'd love to connect you with the Nodus Decoded team. "
        "Let me grab a few quick details. 😊\n\nFirst — what's your name?"
    ),
    "ask_email": "Nice to meet you, {name}! What's the best email address to reach you?",
    "ask_requirement": (
        "Perfect. Lastly — can you briefly describe what you're looking for? "
        "(e.g. 'Need a landing page + SEO for my startup')"
    ),
    "complete": (
        "Thank you, {name}! 🎉 I've passed your details to the Nodus Decoded team. "
        "Someone will reach out to {email} within 1–2 business days. "
        "Is there anything else I can help you with?"
    ),
    "invalid_email": "That doesn't look like a valid email. Could you double-check it?",
}

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def _is_valid_email(value: str) -> bool:
    return bool(EMAIL_REGEX.match(value.strip()))


def get_lead_state(session_id: str) -> dict | None:
    """Return current lead capture state for session, or None if not in flow."""
    return _lead_states.get(session_id)


def start_lead_flow(session_id: str) -> str:
    """
    Called when intent == 'lead' and no active lead flow exists.
    Initialises state and returns the first bot message.
    """
    _lead_states[session_id] = {
        "state": "ask_name",
        "name": None,
        "email": None,
        "requirement": None,
    }
    return MESSAGES["start"]


async def advance_lead_flow(session_id: str, user_input: str) -> Tuple[str, bool]:
    """
    Advance the lead capture state machine by one step.

    Returns:
        (bot_message, is_complete)
        is_complete=True triggers DB write and state cleanup
    """
    state = _lead_states.get(session_id)
    if not state:
        # Shouldn't happen, but handle gracefully
        return start_lead_flow(session_id), False

    current = state["state"]

    if current == "ask_name":
        state["name"] = user_input.strip()[:100]
        state["state"] = "ask_email"
        return MESSAGES["ask_email"].format(name=state["name"]), False

    elif current == "ask_email":
        if not _is_valid_email(user_input):
            return MESSAGES["invalid_email"], False
        state["email"] = user_input.strip().lower()
        state["state"] = "ask_requirement"
        return MESSAGES["ask_requirement"], False

    elif current == "ask_requirement":
        state["requirement"] = user_input.strip()[:1000]
        state["state"] = "complete"

        # Write to Supabase
        try:
            await save_lead(
                session_id=session_id,
                name=state["name"],
                email=state["email"],
                requirement=state["requirement"],
            )
            logger.info(f"Lead saved for {state['email']}")
        except Exception as e:
            logger.error(f"Failed to save lead: {e}")
            # Don't block the user — still confirm and fail silently

        reply = MESSAGES["complete"].format(
            name=state["name"],
            email=state["email"],
        )
        # Clean up state (keep name/email for reference but mark complete)
        _lead_states.pop(session_id, None)
        return reply, True

    # Shouldn't reach here
    return "Something went wrong. Let's start over!", False