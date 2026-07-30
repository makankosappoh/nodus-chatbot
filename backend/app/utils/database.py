"""
app/utils/database.py
---------------------
PostgreSQL connection using SQLAlchemy.
Replaces Supabase entirely.
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, text
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create engine once
engine = create_engine(settings.database_url)


def init_db():
    """
    Create tables if they don't exist.
    Run once on startup.
    """
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                requirement TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conversation_logs (
                id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_msg TEXT NOT NULL,
                bot_reply TEXT NOT NULL,
                intent TEXT,
                latency_ms INTEGER,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """))
        conn.commit()
    logger.info("✅ PostgreSQL tables ready")


async def save_lead(
    session_id: str,
    name: str,
    email: str,
    requirement: str,
    phone: Optional[str] = None,
) -> dict:
    with engine.connect() as conn:
        # Check if email already exists
        existing = conn.execute(text("""
            SELECT id FROM leads WHERE email = :email
        """), {"email": email}).fetchone()

        if existing:
            logger.info(f"Lead already exists for {email} — skipping insert")
            return {"id": existing[0]}

        # Insert new lead
        result = conn.execute(text("""
            INSERT INTO leads (session_id, name, email, phone, requirement)
            VALUES (:session_id, :name, :email, :phone, :requirement)
            RETURNING id
        """), {
            "session_id": session_id,
            "name": name,
            "email": email,
            "phone": phone,
            "requirement": requirement,
        })
        conn.commit()
        row = result.fetchone()
        logger.info(f"Lead saved: {email}")
        return {"id": row[0]}


async def log_conversation(
    session_id: str,
    user_msg: str,
    bot_reply: str,
    intent: str,
    latency_ms: int,
) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO conversation_logs
                (session_id, user_msg, bot_reply, intent, latency_ms)
                VALUES (:session_id, :user_msg, :bot_reply, :intent, :latency_ms)
            """), {
                "session_id": session_id,
                "user_msg": user_msg[:2000],
                "bot_reply": bot_reply[:4000],
                "intent": intent,
                "latency_ms": latency_ms,
            })
            conn.commit()
    except Exception as e:
        logger.warning(f"Conversation log failed: {e}")