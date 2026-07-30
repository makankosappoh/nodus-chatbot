"""
app/core/session.py
-------------------
In-memory session store.
Each session_id (UUID from frontend) holds the last N conversation turns.
"""

from collections import deque
from typing import Dict, List
from app.core.config import settings


# {session_id: deque of {"role": "user"|"assistant", "content": str}}
_sessions: Dict[str, deque] = {}


def get_history(session_id: str) -> List[dict]:
    """Return conversation history for this session as a plain list."""
    return list(_sessions.get(session_id, deque()))


def append_turn(session_id: str, role: str, content: str) -> None:
    """
    Add one turn to session history.
    role must be "user" or "assistant".
    History is capped at settings.context_window_turns * 2
    (each turn = 1 user + 1 assistant message).
    """
    if session_id not in _sessions:
        _sessions[session_id] = deque(maxlen=settings.context_window_turns * 2)
    _sessions[session_id].append({"role": role, "content": content})


def clear_session(session_id: str) -> None:
    """Wipe history for this session (e.g. user clicks 'New chat')."""
    _sessions.pop(session_id, None)