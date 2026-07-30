"""
app/api/chat.py
---------------
POST /api/chat  — main chat endpoint with SSE streaming
POST /api/chat/sync — non-streaming version (for testing / Botpress webhook)
DELETE /api/chat/{session_id} — clear session history
"""

import time
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.core.session import get_history, append_turn, clear_session
from app.rag.intent import classify_intent
from app.rag.chain import generate_response
from app.rag.lead_flow import get_lead_state, start_lead_flow, advance_lead_flow
from app.utils.database import log_conversation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


# ── Fallback response ─────────────────────────────────────────────────────────
# Returned when intent == "fallback" (out of scope query)
FALLBACK_MESSAGE = (
    "I'm Nodus AI, here to help with questions about Nodus Decoded's digital "
    "services — web design, SEO, performance marketing, and more. "
    "I'm not able to help with that particular question, but I'd love to tell "
    "you about what we offer! What would you like to know? 😊"
)


# ── SSE streaming endpoint ────────────────────────────────────────────────────

@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """
    SSE streaming chat endpoint.
    Frontend connects with EventSource and receives tokens as they generate.

    Response format:
        data: <token>\n\n    ← each token chunk
        data: [DONE]\n\n     ← signals stream end
    """
    start_time = time.time()
    session_id = req.session_id
    message = req.message.strip()

    logger.info(f"[{session_id[:8]}] Received: '{message[:60]}'")

    # Check if we're already in a lead capture flow for this session
    active_lead = get_lead_state(session_id)

    async def event_generator():
        full_reply = ""
        resolved_intent = "general"

        try:
            if active_lead:
                # ── Route B: Active lead flow ─────────────────────────────
                resolved_intent = "lead"
                reply, _ = await advance_lead_flow(session_id, message)
                full_reply = reply
                yield {"data": reply}

            else:
                # ── Classify intent ───────────────────────────────────────
                intent = classify_intent(message)
                resolved_intent = intent

                if intent == "fallback":
                    # ── Route C: Out of scope ─────────────────────────────
                    full_reply = FALLBACK_MESSAGE
                    yield {"data": FALLBACK_MESSAGE}

                elif intent == "lead":
                    # ── Route B: Start lead capture ───────────────────────
                    reply = start_lead_flow(session_id)
                    full_reply = reply
                    yield {"data": reply}

                else:
                    # ── Route A: RAG pipeline ─────────────────────────────
                    history = get_history(session_id)
                    async for token in generate_response(message, history):
                        full_reply += token
                        yield {"data": token}

        except Exception as e:
            logger.error(f"Stream error for [{session_id[:8]}]: {e}")
            err_msg = "Something went wrong. Please try again!"
            full_reply = err_msg
            yield {"data": err_msg}

        finally:
            # Signal end of stream
            yield {"data": "[DONE]"}

            # Persist turns to session memory
            append_turn(session_id, "user", message)
            append_turn(session_id, "assistant", full_reply)

            # Log to Supabase (fire-and-forget, non-blocking)
            latency_ms = int((time.time() - start_time) * 1000)
            try:
                await log_conversation(
                    session_id=session_id,
                    user_msg=message,
                    bot_reply=full_reply,
                    intent=resolved_intent,
                    latency_ms=latency_ms,
                )
            except Exception as e:
                logger.warning(f"Log failed (non-critical): {e}")

    return EventSourceResponse(event_generator())


# ── Non-streaming fallback ────────────────────────────────────────────────────

@router.post("/sync", response_model=ChatResponse)
async def chat_sync(req: ChatRequest):
    """
    Non-streaming version — collects full response then returns JSON.
    Use this for Botpress webhook integration or API testing.
    """
    start_time = time.time()
    session_id = req.session_id
    message = req.message.strip()

    active_lead = get_lead_state(session_id)
    full_reply = ""
    resolved_intent = "general"

    if active_lead:
        resolved_intent = "lead"
        full_reply, _ = await advance_lead_flow(session_id, message)

    else:
        intent = classify_intent(message)
        resolved_intent = intent

        if intent == "fallback":
            full_reply = FALLBACK_MESSAGE

        elif intent == "lead":
            full_reply = start_lead_flow(session_id)

        else:
            history = get_history(session_id)
            async for token in generate_response(message, history):
                full_reply += token

    append_turn(session_id, "user", message)
    append_turn(session_id, "assistant", full_reply)

    latency_ms = int((time.time() - start_time) * 1000)
    await log_conversation(session_id, message, full_reply, resolved_intent, latency_ms)

    return ChatResponse(
        session_id=session_id,
        reply=full_reply,
        intent=resolved_intent,
    )


# ── Clear session ─────────────────────────────────────────────────────────────

@router.delete("/{session_id}")
async def clear_chat_session(session_id: str):
    clear_session(session_id)
    return {"message": f"Session {session_id} cleared"}