"""
app/rag/intent.py
-----------------
One-shot intent classifier using Gemini Flash.

Routes every user message into one of three buckets:
    - "general"  → pass to RAG pipeline
    - "lead"     → trigger lead capture conversational flow
    - "fallback" → hard-coded polite decline (out of scope)

This is a single cheap LLM call (~50 tokens) before the heavier RAG call.
"""

import re
import logging
from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

# Intent type alias used across the app
IntentType = Literal["general", "lead", "fallback"]

# ── System prompt for intent classification ──────────────────────────────────
# Keep this tightly scoped — it should ONLY classify, never answer.
INTENT_SYSTEM_PROMPT = """You are an intent classifier for Nodus Decoded, a digital agency.

Classify the user message into EXACTLY one of these three categories:

1. general   → The user is asking about services, pricing, portfolio, process,
                team, timelines, technologies used, or any factual question
                about Nodus Decoded.

2. lead      → The user signals they want to hire, work with, or contact Nodus.
                Keywords: "hire", "work with you", "need a website",
                "proposal", "book", "consult", "talk to someone",
                "I need [service]", "how much will it cost for my project".

3. fallback  → The message is completely unrelated to Nodus Decoded or digital
                agency services (e.g. weather, coding homework, personal questions).

Reply with ONLY the single word: general, lead, or fallback.
Do not explain. Do not add punctuation.
"""


def classify_intent(message: str) -> IntentType:
    """
    Classify a user message into general / lead / fallback.
    Returns the intent string.

    Uses Gemini Flash with low temperature for deterministic output.
    Cost: ~50 input tokens + 1 output token per call.
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=str(settings.groq_api_key),
        temperature=0.0,
        max_tokens=5,  # deterministic — we want consistent classification
        max_retries=0,
    )

    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=f"User message: {message}"),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content.strip().lower()

        # Guard: extract just the keyword in case Gemini adds punctuation
        for intent in ("general", "lead", "fallback"):
            if intent in raw:
                logger.info(f"Intent classified: {intent} | message='{message[:60]}'")
                return intent

        # Default to general if classifier returns something unexpected
        logger.warning(f"Unexpected classifier output: '{raw}' — defaulting to general")
        return "general"

    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return "general"  # safe fallback: let RAG handle it