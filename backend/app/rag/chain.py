"""
app/rag/chain.py
----------------
Builds the full RAG chain: context injection → Gemini → streamed response.

This is the core of Phase 3. The flow per request:
    1. retrieve() fetches top-k chunks from ChromaDB
    2. If chunks found → build grounded prompt with context
    3. If no chunks → fall back to FAQ JSON exact match
    4. Call Gemini Flash and stream back tokens via async generator

The system prompt is the anti-hallucination gate:
Gemini is told it MUST answer from the retrieved context only.
"""

import json
import logging
import os
from typing import AsyncGenerator, List
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.rag.retriever import retrieve

logger = logging.getLogger(__name__)

# ── System prompt ─────────────────────────────────────────────────────────────
# IMPORTANT: When you have real Nodus content, update lines marked [NODUS INFO]
# to match the actual agency name, services, and tone.

SYSTEM_PROMPT_TEMPLATE = """You are Nodus AI, the official assistant for Nodus Decoded — \
a full-service digital agency.

Your job is to help website visitors understand Nodus Decoded's services, pricing, \
process, and portfolio — and to collect contact details from interested clients.

── STRICT RULES ──────────────────────────────────────────────────────────────
1. ONLY answer using the CONTEXT provided below. Do not use your own training data
    to answer questions about Nodus Decoded.
2. If the context does not contain enough information to answer confidently,
    say: "I don't have that specific detail right now — our team can answer this
    directly. Would you like to leave your contact details?"
3. NEVER invent services, prices, timelines, or client names that aren't in the context.
4. Keep answers concise (2–4 sentences for simple questions, bullet points for lists).
5. Always be helpful, professional, and encouraging — you represent Nodus Decoded.
6. If the user seems ready to hire or inquire, invite them to share their details.

── CONTEXT FROM KNOWLEDGE BASE ───────────────────────────────────────────────
{context}
──────────────────────────────────────────────────────────────────────────────

Answer the user's question based strictly on the context above."""


def _load_faq_fallback() -> dict:
    """
    Load the FAQ JSON fallback database.
    Returns dict of {question_keyword: answer} pairs.
    This file is created in Week 1-2 — see knowledge_base/raw/faq.json
    """
    faq_path = os.path.join(
        os.path.dirname(__file__), "../../knowledge_base/raw/faq.json"
    )
    if not os.path.exists(faq_path):
        logger.warning("faq.json not found — FAQ fallback disabled")
        return {}
    with open(faq_path, "r") as f:
        data = json.load(f)
    # Expect format: [{"q": "...", "a": "..."}, ...]
    return {item["q"].lower(): item["a"] for item in data.get("faqs", [])}


def _faq_lookup(query: str, faq: dict) -> str | None:
    """
    Simple keyword-based FAQ lookup.
    Returns matched answer or None.
    Replace with fuzzy match (rapidfuzz) if you want better accuracy.
    """
    query_lower = query.lower()
    for question, answer in faq.items():
        # Check if enough keywords from the FAQ question appear in user query
        keywords = [w for w in question.split() if len(w) > 3]
        matches = sum(1 for kw in keywords if kw in query_lower)
        if keywords and matches / len(keywords) >= 0.5:
            return answer
    return None


async def generate_response(
    message: str,
    history: List[dict],
) -> AsyncGenerator[str, None]:
    """
    Main RAG chain — yields token strings for SSE streaming.

    Usage in route handler:
        async for token in generate_response(msg, history):
            yield f"data: {token}\\n\\n"
    """
    # Step 1: Retrieve relevant chunks
    chunks: List[Document] = retrieve(message)

    # Step 2: If no chunks above threshold → try FAQ fallback
    if not chunks:
        faq = _load_faq_fallback()
        faq_answer = _faq_lookup(message, faq)
        if faq_answer:
            logger.info("Serving answer from FAQ fallback")
            # Yield as single token for consistency with streaming interface
            yield faq_answer
            return

    # Step 3: Build context string from retrieved chunks
    if chunks:
        context_parts = []
        for i, doc in enumerate(chunks, 1):
            source = doc.metadata.get("source", "unknown")
            context_parts.append(f"[{i}] (source: {source})\n{doc.page_content}")
        context = "\n\n".join(context_parts)
    else:
        # No chunks AND no FAQ match → tell Gemini context is empty
        # System prompt handles this case gracefully
        context = "No specific context available for this query."
        logger.info("No RAG context found — Gemini will use fallback response")

    # Step 4: Build the full prompt
    filled_system = SYSTEM_PROMPT_TEMPLATE.format(context=context)

    # Step 5: Build message list with conversation history
    messages = [SystemMessage(content=filled_system)]

    # Add prior conversation turns (last N turns from session)
    for turn in history:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            # LangChain uses AIMessage for assistant turns
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=content))

    # Add current user message
    messages.append(HumanMessage(content=message))

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=str(settings.groq_api_key),
        temperature=0.3,       # slightly creative but mostly factual
        max_tokens=800, # enough for a detailed answer, not a novel
        max_retries=0,
    )

    try:
        full_response = ""
        async for chunk in llm.astream(messages):
            token = chunk.content
            if token:
                full_response += token
                yield token
    except Exception as e:
        logger.error(f"Gemini streaming error: {e}")
        yield "Sorry, I'm having trouble connecting right now. Please try again in a moment."